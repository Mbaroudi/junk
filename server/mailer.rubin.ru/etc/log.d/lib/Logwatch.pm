#!/usr/bin/perl
#
# $Id: Logwatch.pm,v 1.8 2005/02/24 17:06:57 kirk Exp $

package Logwatch;

use strict;
use Exporter;

=pod

=head1 NAME

Logwatch -- Utility functions for Logwatch Perl modules.

=head1 SYNOPSIS

 use Logwatch ':sort';

 ##
 ## Show CountOrder()
 ##

 # Sample Data
 my %UnknownUsers = (jb1o => 4, eo00 => 1, ma3d => 4, dr4b => 1);
 my $sortClosure = CountOrder(%UnknownUsers);
 foreach my $user (sort $sortClosure keys %UnknownUsers) {
     my $plural = ($UnknownUsers{$user} > 1) ? "s" : "";
     printf "  %-8s : %2d time%s\n", $user, $UnknownUsers{$user}, $plural;
 }

 ##
 ## Show TotalCountOrder()
 ##

 # Sample Data
 my %RelayDenied = ( some.server  => {you@some.where => 2, foo@bar.com => 4},
		     other.server => { foo@bar.com => 14 }
		   );

 my $sub = TotalCountOrder(%RelayDenied);
 foreach my $relay (sort $sub keys %RelayDenied) {
     print "    $relay:\n";
     my $countOrder = CountOrder(%{$RelayDenied{$relay}});
     foreach my $dest (sort $countOrder keys %{$RelayDenied{$relay}}) {
         my $plural = ($RelayDenied{$relay}{$dest} > 1) ? "s" : "";
         printf "        %-36s: %3d Time%s\n", $dest,
     	     $RelayDenied{$relay}{$dest}, $plural;
     }
 }

 use Logwatch ':ip';

 ##
 ## Show SortIP()
 ##

 # Sample Data
 @ReverseFailures = qw{10.1.1.1 172.16.1.1 10.2.2.2 192.168.1.1 };
 @ReverseFailures = sort SortIP @ReverseFailures;
 { local $" = "\n  "; print "Reverse DNS Failures:\n  @ReverseFailures\n" }

	-or-

 ##
 ## Show LookupIP()
 ##
 foreach my $ip (sort SortIP @ReverseFailures) {
     printf "%15s : %s\n", $ip, LookupIP($ip);
 }

=head1 DESCRIPTION

This module provides utility functions intended for authors of Logwatch
scripts. The purpose is to abstract commonly performed actions into a
set of generally available subroutines. The subroutines can optionally
be imported into the local namespace.

=over 4

=cut

our @ISA = qw{Exporter};
our @EXPORT;
our @EXPORT_OK;
our %EXPORT_TAGS = (sort => [qw(CountOrder TotalCountOrder SortIP)],
		    ip   => [qw(LookupIP SortIP)]);

Exporter::export_ok_tags(qw{sort ip});

$EXPORT_TAGS{all} = [@EXPORT, @EXPORT_OK];

=pod

=item I<CountOrder(%hash [, $coderef ])>

This function returns a closure suitable to be passed to Perl's C<sort>
builtin. When two values are passed to the closure, it compares the
numeric values of those keys in C<%hash>, and if they're equal, the
lexically order of the keys. Thus:

  my $sortClosure = CountOrder(%UnknownUsers);
  foreach my $user (sort $sortClosure keys %UnknownUsers) {
      my $plural = ($UnknownUsers{$user} > 1) ? "s" : "";
      printf "  %-8s : %2d time%s\n", $user, $UnknownUsers{$user}, $plural;
  }

Will print the keys and values of C<%UnknownUsers> in frequency order,
with keys of equal values sorted lexically.

The optional second argument is a coderef to be used to sort the keys in
an order other than lexically. (a reference to C<SortIP>, for example.)

=cut

# Use a closure to abstract the sort algorithm
sub CountOrder(\%;&) {
    my $href = shift;
    my $coderef = shift;
    return sub {
	# $a & $b are in the caller's namespace, moving this inside
	# guarantees that the namespace of the sort is used, in case
	# it's different (admittedly, that's highly unlikely), at a
	# miniscule performance cost.
	my $package = (caller)[0];
	no strict 'refs'; # Back off, man. I'm a scientist.
	my $A = $ {"${package}::a"};
	my $B = $ {"${package}::b"};
	use strict 'refs'; # We are a hedge. Please move along.
	# Reverse the count, but not the compare
	my $count = $href->{$B} <=> $href->{$A};
	return $count if $count;
	if (ref $coderef) {
	    $a = $A;
	    $b = $B;
	    &$coderef();
	} else {
	    ($A cmp $B);
	}
    }
}

=pod

=item I<TotalCountOrder(%hash [, $coderef ])>

This function returns a closure similar to that returned by
C<CountOrder()>, except that it assumes a hash of hashes, and totals the
keys of each sub hash. Thus:

 my $sub = TotalCountOrder(%RelayDenied);
 foreach my $relay (sort $sub keys %RelayDenied) {
     print "    $relay:\n";
     my $countOrder = CountOrder(%{$RelayDenied{$relay}});
     foreach my $dest (sort $countOrder keys %{$RelayDenied{$relay}}) {
         my $plural = ($RelayDenied{$relay}{$dest} > 1) ? "s" : "";
         printf "        %-36s: %3d Time%s\n", $dest,
     	     $RelayDenied{$relay}{$dest}, $plural;
     }
 }

Will print the relays in the order of their total denied destinations
(equal keys sort lexically), with each sub hash printed in frequency
order (equal keys sorted lexically)

The optional second argument is a coderef to be used to sort the keys in
an order other than lexically. (a reference to C<SortIP>, for example.)

=cut

sub TotalCountOrder(\%;&) {
    my $href = shift;
    my $coderef = shift;
    my $cache = {};
    return sub {
	# $a & $b are in the caller's namespace, moving this inside
	# guarantees that the namespace of the sort is used, in case
	# it's different (admittedly, that's highly unlikely), at a
	# miniscule performance cost.
	my $package = (caller)[0];
	no strict 'refs'; # Back off, man. I'm a scientist.
	my $A = $ {"${package}::a"};
	my $B = $ {"${package}::b"};
	use strict 'refs'; # We are a hedge. Please move along.
	my ($AA, $BB);

	foreach my $tuple ( [\$A, \$AA], [\$B, \$BB] ) {
	    my $keyRef = $tuple->[0];
	    my $totalRef = $tuple->[1];

	    if (exists($cache->{$$keyRef})) {
		$$totalRef = $cache->{$$keyRef};
	    } else {
		grep {$$totalRef += $href->{$$keyRef}->{$_}}
		    keys %{$href->{$$keyRef}};
		$cache->{$$keyRef} = $$totalRef;
	    }
	}
	my $count = $BB <=> $AA;
	
	return $count if $count;
	if (ref $coderef) {
	    $a = $A;
	    $b = $B;
	    &$coderef();
	} else {
	    ($A cmp $B);
	}
    }
}

=pod

=item I<SortIP>

This function is meant to be passed to the perl C<sort> builtin. It
sorts a list of "dotted quad" IP addresses by the values of the
individual octets.

=cut

sub canonical_ipv6_address {
    my @a = split /:/, shift;
    my @b = qw(0 0 0 0 0 0 0 0);
    my $i = 0;
    while (defined $a[0] and $a[0] ne '') {$b[$i++] = shift @a;}
    @a = reverse @a;
    $i = 7;
    while (defined $a[0] and $a[0] ne '') {$b[$i--] = shift @a;}
    @b;
}

sub SortIP {
    # $a & $b are in the caller's namespace.
    my $package = (caller)[0];
    no strict 'refs'; # Back off, man. I'm a scientist.
    my $A = $ {"${package}::a"};
    my $B = $ {"${package}::b"};
    $A =~ s/^::(ffff:)?(\d+\.\d+\.\d+\.\d+)$/$2/;
    $B =~ s/^::(ffff:)?(\d+\.\d+\.\d+\.\d+)$/$2/;
    use strict 'refs'; # We are a hedge. Please move along.
    if ($A =~ /:/ and $B =~ /:/) {
	my @a = canonical_ipv6_address($A);
	my @b = canonical_ipv6_address($B);
	while ($a[1] and $a[0] == $b[0]) {shift @a; shift @b;}
	$a[0] <=> $b[0];
    } elsif ($A =~ /:/) {
	-1;
    } elsif ($B =~ /:/) {
	1;
    } else {
        my ($a1, $a2, $a3, $a4) = split /\./, $A;
        my ($b1, $b2, $b3, $b4) = split /\./, $B;
        $a1 <=> $b1 || $a2 <=> $b2 || $a3 <=> $b3 || $a4 <=> $b4;
    }
}

=pod

=item I<LookupIP($dottedQuadIPaddress)>

This function performs a hostname lookup on a passed in IP address. It
returns the hostname (with the IP in parentheses) on success and the IP
address on failure. Results are cached, so that many calls with the same
argument don't tax the resolver resources.

For (new) backward compatibility, this function now uses the $DoLookup
variable in the caller's namespace to determine if lookups will be made.

=cut

# Might as well cache it for the duration of the run
my %LookupCache = ();

sub LookupIP {
   my $Addr = $_[0];

   # OOPS! The 4.3.2 scripts have a $DoLookup variable. Time for some
   # backwards compatible hand-waving.

   # for 99% of the uses of this function, assuming package 'main' would
   # be sufficient, but a good perl hacker designs so that the other 1%
   # isn't in for a nasty suprise.
   my $pkg = (caller)[0];

   # Default to true
   my $DoLookup = 1;
   {
       # An eval() here would be shorter (and probably clearer to more
       # people), but QUITE a bit slower. This function should be
       # designed to be called a lot, so efficiency is important.
       local *symTable = $main::{"$pkg\::"};

       # here comes the "black magic," (this "no" is bound to the
       # enclosing block)
       no strict 'vars';
       if (exists $symTable{'DoLookup'} && defined $symTable{'DoLookup'}) {
	   *symTable = $symTable{'DoLookup'};
	   $DoLookup = $symTable;
       }
   }

   return $Addr unless($DoLookup);

   return $LookupCache{$Addr} if exists ($LookupCache{$Addr});

   if ($Addr =~ /:/ and $Addr !~ /^::ffff:(\d+\.\d+\.\d+\.\d+)/) {
       return "unresolved IPv6 addr: $Addr";
   }
   $Addr =~ s/::ffff://;
   my $PackedAddr = pack('C4', split /\./,$Addr);
   if (my $name = gethostbyaddr ($PackedAddr,2)) {
       my $val = "$name ($Addr)";
       $LookupCache{$Addr} = $val;
       return $val;
   } else {
       $LookupCache{$Addr} = $Addr;
       return ($Addr);
   }
}

=pod

=back

=head1 TAGS

In addition to importing each function name explicitly, the following
tags can be used.

=over 4

=item I<:sort>

Imports C<CountOrder>, C<TotalCountOrder and C<SortIP>

=item I<:ip>

Imports C<SortIP> and C<LookupIP>

=item I<:all>

Imports all importable symbols.

=cut

1;

# vi: shiftwidth=3 tabstop=3 et

