# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo-src/rc-scripts/init.d/shutdown.sh,v 1.11.4.3 2005/05/16 23:58:05 vapier Exp $

/sbin/halt -ihdp

# hmm, if the above failed, that's kind of odd ...
# so let's force a halt
/sbin/halt -f
