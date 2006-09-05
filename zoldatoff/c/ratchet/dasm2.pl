#!/usr/bin/perl -w

# dasm2 - Linux disassembler v2
# Copyright (C) 2002 - J.W. Janssen (JanWillem.Janssen@lxtreme.nl)
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


# This script is based on the original `dasm.pl' script by 
# SiuL+Hacky from July 1999. 
#
# This version is a rewrite of the original script to make it
# strict and warning free. Furthermore, this version is able to
# interleave any found debug information into the source. Source
# output is completely cross referenced and added with comments.

use warnings qw(all);
use strict;
use Carp;
use Getopt::Long;

# Parameters
my ( $quiet, $prefix_address, $output_file ) = ( undef, 0, '-' );
# Global used variables ...
my $unistd_file = "/usr/src/linux/include/asm-i386/unistd.h";

GetOptions( 'quiet' => \$quiet,
	    'prefix!' => \$prefix_address,
	    'unistd=s' => \$unistd_file,
	    'output=s' => \$output_file );

# Force the quiet output if we're dumping to STDOUT...
$quiet = 1 if $output_file eq '-';

my $progname = `basename $0`; chop $progname;
my $version = "1.2a";

my ( $prefix, @sections, %dasm_info, %meta_info, @output );
my ( $index, $progress_index, @progress ) = ( 0, 0, qw/. o 0 O 0 o/ );
my $pass = 0;

# The long texts for the sections
my %section_names = (
	".bss" => "unitialized data",
	".comment" => "version control information",
	".data" => "initialized data",
	".debug" => "symbolic debugging information",
	".dynamic" => "dymanic linking information",
	".dynstr" => "dynamic strings table",
	".dynsym" => "dynamic symbol table",
	".fini" => "process termination code",
	".got" => "global offset table",
	".hash" => "symbol hash table",
	".init" => "process initialization code",
	".interp" => "program interpreter",
	".line" => "symbolic debugging information",
	".note" => "information",
	".plt" => "procedure linking table",
	".rel" => "relocation information",
	".rodata" => "read-only data (constants)",
	".shstrtab" => "section names",
	".strtab" => "strings table",
	".symtab" => "symbol table",
	".text" => "actual program code" );

# Check for the right amount of parameters ...
die usage() unless $#ARGV == 0 and ( -f $ARGV[ 0 ] );
my ( $input_file ) = ( @ARGV );

# Make sure we've got something to parse...
die usage() . "\n$1\n"
	if ( (`objdump -a $input_file 2>&1`)[ 0 ] =~ m/^objdump: (.*)$/ );

# Print some nice information about what we're doing...
message( "\nCreating disassembled file ($input_file => ".
	 ($output_file eq '-' ? "screen" : $output_file).") ...\n" );

# Obtain the different sources of information ...
pass( "Obtaining raw section information" );
my @section_info = `objdump -afph $input_file 2>&1`;

pass( "Obtaining raw symbol information" );
my @symbol_tables = `objdump -tT $input_file 2>&1`;

if ( -f $unistd_file )
{
  pass( "Obtaining system call information" );
  foreach ( grep { /#define\s+__NR_/ } `cat $unistd_file` )
  {
    /__NR_(.+?)\s+(\d+)\s+?/ and $meta_info{ syscalls }{ $2 } = $1;
  }
}
else
{
  carp "WARNING: Couldn't obtain system call information from $unistd_file\n";
}

pass( "Obtaining raw disassembled source" .
	( -s $input_file > 400000 ? " (may take a while)" : "" ) );
my @source = `objdump -dSC --prefix-address $input_file 2>&1`;

carp "WARNING: $1\n" if ( $source[ 0 ] =~ m/^objdump: (.*)$/ );

# Obtain information about the location of the RO data in the object...
my @rodata_info = grep( /\d+\s+\.rodata/, @section_info );

# Init these, in case we're not having a .rodata section (like raw 
#	coded assembly) ...
$meta_info{ rodata }{ start_address } = 0;
$meta_info{ rodata }{ end_address } = 0;
$meta_info{ rodata }{ strings } = 0;

message( "Progress: " );
if ( defined $rodata_info[ 0 ] and
     $rodata_info[ 0 ] =~ /\d+\s+\.rodata\s+(\S+)  (\S+)  (\S+)  (\S+)/g )
{
  pass( "Obtaining string information" );

  # Progress meter...
  message( progress() );

  # Store this for later use...
  $meta_info{ rodata }{ start_address } = hex( $2 );
  $meta_info{ rodata }{ end_address } =
			$meta_info{ rodata }{ start_address } + hex( $1 );

  open CODE, "<$input_file";
  seek CODE, hex( $4 ), 0;
  read CODE, $meta_info{ rodata }{ strings }, hex( $1 );
  close CODE;
}

# Obtain the symbol table and its information...
pass( "Processing symbol table(s)" );
message( "Progress: " );
$prefix = 1;

foreach ( @symbol_tables )
{
  chop;

  # Progress meter...
  message( progress() );

  # There's a nasty header prefixed to every output of objdump...
  $prefix = 0 if /^(.*)SYMBOL TABLE:$/;
  next if $prefix == 1 or /SYMBOL TABLE:$/ or /^$/;

  my @info = split /\s+/;
  my $address = hex( shift @info );

  $meta_info{ symbol_tables }{ $address } = \@info;
}

# Process the object code for JMPs and CALLs ...
pass( "Cross referencing object code" );
message( "Progress: " );
my ( $section, $move_eax, @info ) = ( "", "" );
$prefix = 1;

foreach ( @source )
{
  chop;

  # Strip out all unwanted / unnecessary information ...
  s/0x//g;
  s/<.*?>//g;
  s/\s+/ /g;

  # Progress meter...
  message( progress() );

  # There's a nasty header prefixed to every output of objdump...
  $prefix = 0, $section = $1 if /^Disassembly of section (.*):$/;
  next if $prefix == 1 or /^Disassembly of section/;

  # Store the sections ordering for later use...
  push @sections, $section if not exists $dasm_info{ $section };

  # Check if the line begins with an address (if not, it could be 
  #	debugging information...
  if ( /^[0-9a-fA-F]{8} / )
  {
    push @{$dasm_info{ $section }}, $_;
    # info[0] = address, info[1] = operator, info[2] = operand
    @info = split /\s+/;
  }
  else
  {
    push @{$dasm_info{ debug }{ hex( $info[ 0 ] ) }}, $_;
  }

  # Look for (un)conditional jumps ...
  if ( $info[ 1 ] =~ /(j\w+|call)/ )
  {
    my $target_key = ( $1 eq 'call' ? 'calls' : 'jumps' );

    if ( $info[ 2 ] =~ /^\*?([0-9a-fA-F]+)$/ )
    {
      $meta_info{ $target_key }{ hex( $1 ) } .= ( $info[ 0 ] . '; ' );

      # If possible try to obtain the symbolic name of the called address
      if ( defined $meta_info{ symbol_tables }{ hex( $1 ) } )
      {
        my @symbol_info = @{ $meta_info{ symbol_tables }{ hex( $1 ) } };
	my $prefix = substr( $target_key, 0, length( $target_key ) - 1 );

	if ( $section eq ".plt" and $symbol_info[ $#symbol_info ] == 0 )
	{
	  $meta_info{ function_calls }{ hex( $info[ 0 ] ) } =
			$prefix . " to external LIBC function";
	}
	else
	{
	  $meta_info{ function_calls }{ hex( $info[ 0 ] ) } =
			$prefix . " to " . $symbol_info[ $#symbol_info ];
	}
      }
    }
  }

  # Store ``mov val,%eax'' for later use...
  if ( $info[ 1 ] =~ /mov/ and $info[ 2 ] =~ /\$([0-9a-fA-F]+),\%eax/ )
  {
    $move_eax = $meta_info{ syscalls }{ hex( $1 ) };
  }
  
  # Look for Linux system calls (int $80) ...
  if ( $info[ 1 ] =~ /int/ and $info[ 2 ] =~ /\$80/ )
  {
    $meta_info{ interrupts }{ hex( $info[ 0 ] ) } = "System call: $move_eax"
    				if defined $move_eax;
  }

  # Look for references to data ...
  if ( /\$\d/ )
  {
    my ( $instruction, $operand, $rest ) = split /\$/, $_, 2;
    if ( !/push/ )
    {
      ( $operand, $rest ) = split /\,/, $operand, 2;
    }

    my $offset = hex( $operand );
    if ( $offset <= $meta_info{ rodata }{ end_address } and
    	 $offset >= $meta_info{ rodata }{ start_address } )
    {
      # Obtain the exact string that's been referenced...
      my $auxiliar = substr( $meta_info{ rodata }{ strings },
      			     $offset - $meta_info{ rodata }{ start_address } );
      my $length = index( $auxiliar, pack( 'x' ) );
      $auxiliar = substr( $auxiliar, 0, $length );
      $auxiliar =~ s/\n//g;

      # Store this for later use...
      $meta_info{ strref }{ hex( $info[ 0 ] ) } = $auxiliar;
    }
    elsif ( defined $meta_info{ symbol_tables }{ $offset } )
    {
      # Perhaps, we're calling data?
      my @extra = @{ $meta_info{ symbol_tables }{ $offset } };
      # FIXME: Should be stored in another section?
      $meta_info{ strref }{ hex( $info[ 0 ] ) } = $extra[ $#extra ];
    }
  }
}

pass( "Writing cross referenced object code" );

carp "\rWARNING: Overwriting output file\n" if ( -f $output_file );
open OUTPUT, ">$output_file";

print OUTPUT "; $input_file - extended data dump\n";
print OUTPUT "; created by $progname ($^O) on " . localtime(time) . "\n\n";

print OUTPUT "; Header information:\n";
print OUTPUT ";   " . $section_info[ $_ ] for ( 3..$#section_info );
#print OUTPUT "; " . $symbol_tables[ $_ ]."\n" for ( 3..$#symbol_tables );

message( "Progress: " );
foreach ( @sections )
{
  my @code = @{ $dasm_info{ $_ } };
  my $suffix;

  print OUTPUT "\n;\n; Disassembly of section $_ (" .
  	$section_names{ $_ } . "):\n;\n";

  foreach ( @code )
  {
    # Progress meter...
    message( progress() );

    my ( $location, $operator, $operands ) = split /\s+/;
    my $address = hex( $location );	# We use decimal address internally...
    $operands = "" unless defined $operands;
    $suffix = ";  ";

    # Start each subroutine with a nice clear header...
    if ( defined $meta_info{ symbol_tables }{ $address } )
    {
      my @symbol_info = @{ $meta_info{ symbol_tables }{ $address } };
      print OUTPUT "\n  ;\n  ; " . $symbol_info[ $#symbol_info ] . "\n  ;\n"
			if ( $symbol_info[ $#symbol_info ] !~ /\d+/ );
    }

    # Check if we've got debug information to insert ...
    if ( defined $dasm_info{ debug }{ $address } )
    {
      my @lines = @{ $dasm_info{ debug }{ $address } };
      print OUTPUT "\n  ; " . join( "\n  ; ", @lines );
      print OUTPUT "\n";
    }

    # Add information about references system calls ...
    if ( defined $meta_info{ interrupts }{ $address } )
    {
      $suffix .= ", " if length $suffix > 4;
      $suffix .= $meta_info{ interrupts }{ $address };
    }

    # Cross reference any destination addresses ...
    if ( defined $meta_info{ function_calls }{ $address } )
    {
      $suffix .= ", " if length $suffix > 4;
      $suffix .= $meta_info{ function_calls }{ $address };
    }

    # Add information about jump references ...
    if ( defined $meta_info{ jumps }{ $address } )
    {
      $suffix .= ", " if length $suffix > 4;
      $suffix .= "referenced from jump(s) at " .
      		 $meta_info{ jumps }{ $address };
    }

    # Add information about call references ...
    if ( defined $meta_info{ calls }{ $address } )
    {
      $suffix .= ", " if length $suffix > 4;
      $suffix .= "referenced from call(s) at " .
      		 $meta_info{ calls }{ $address };
    }

    # Add information about referenced static data ...
    if ( defined $meta_info{ strref }{ $address } and
    	 length $meta_info{ strref }{ $address } )
    {
      $suffix .= ", " if length $suffix > 4;
      $suffix .= "reference to data : \"" .
      		 $meta_info{ strref }{ $address } . "\"";
    }

    $suffix .= "\n" if length $suffix > 4;

    # Output the normal code ...
#    $prefix =
#    	   sprintf( "  %08s  %-6s  %-30s ", $location, $operator, $operands );
#    print OUTPUT "$prefix $suffix\n";
    print OUTPUT make_output_line( $location, $operator, $operands, $suffix );
  }
}

message( "\rDone.                 \n\n" );

close OUTPUT;


### END ### BEGIN EYE-CANDY ROUTINES ### END ### BEGIN EYE-CANDY ROUTINES ###

sub usage
{
  return "$progname v$version" . 
  	 ' - (c) 2002 by JaWi, janwillem.janssen@lxtreme.nl'."\n\n".
  	 "Usage: $progname OPTIONS... <binary input>\n\n".
	 "Where OPTIONS is one of:\n".
	 "   -q(uiet)        Don't print any progress information.\n".
	 "   -p(refix)       Prefix assembly output with source address.\n".
	 "   -nop(refix)     Don't prefix assembly output (default).\n".
	 "   -unistd=<file>  Obtain system call information from this file.\n".
	 "   -output=<file>  Output assembly to <file> (defaults to STDOUT).\n";
} # usage

GetOptions( 'quiet' => \$quiet,
	    'prefix!' => \$prefix_address,
	    'unistd=s' => \$unistd_file,
	    'output=s' => \$output_file );

sub message
{
  print STDERR @_ unless defined $quiet;
} # message

sub pass
{
  print STDERR "\rPass " . ++$pass . " - @_ ...\n" unless defined $quiet;
} # pass


sub progress
{
  if ( ( $progress_index++ % 40 ) == 0 )
  {
    $index = ( ++$index % ( $#progress + 1 ) );
  }

  return $progress[ $index ]."\b";
} # progress


sub make_output_line
{
  my ( $location, $operator, $operands, $suffix ) = @_;

  my $line = "  ";
  if ( $prefix_address == 1 )
  {
    $line = sprintf( "  %08s  ", $location );
  }
  $line .= sprintf( "%-6s  %-30s  %s\n", $operator, $operands, $suffix );

  return $line;
} # make_output_line

