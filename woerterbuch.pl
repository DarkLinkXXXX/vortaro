#!/usr/bin/env perl

# before you start: download dictionary file from dict.cc an rename it as wb.txt
# put it in the same directory as this script.
# ensure that it's encoding is the same as your systems!

# by matthias.bloch at puffin dot ch

# because the code is in German I wrote some comments in English :-)

open (LISTE, "wb.txt") or die "can't load dictionary: $!";
@woerterbuch= <LISTE>;
close LISTE;

$_ =~ s/ß/ss/ foreach (@woerterbuch);	# replace all ß by ss. German users may want to comment this line out. :-)

while (1){
	%treffer = undef;
	$laengstes = 0;
	print "\n\nWelches Wort suchen? ";	# Search which word?
	$was_finden = <STDIN>;
	chomp ($was_finden);
	
	print "*"x(21+length($was_finden));
	print "\n\n";
	
	foreach $e (@woerterbuch){
		if ($e =~ /$was_finden/i){
			
			($englisch, $deutsch) = split (/::/, $e);	# the dictionary is in the form: english_word::german_word
			s/\s$//g foreach ($englisch, $deutsch);   # remove space
			$deutsch =~ s/^\s//g;
			chomp $deutsch;
			$treffer{$englisch}.=", " if (exists $treffer{$englisch});
			$treffer{$englisch}.=$deutsch;
			
			$laengstes = length ($englisch) if ($laengstes < length ($englisch));	
		}
	}
	
	$treffer_anzahl = 0;
	SUCHE:{
		foreach $match ("^$was_finden\$", "^$was_finden\\S", "^$was_finden\\s", ".+\\s$was_finden", "\\S$was_finden"){
			# first it looks for a match, then for a match at the beginning, then a match anywere
			foreach (sort keys %treffer){
				if ($_ =~  /$match/i or $treffer{$_} =~ /$match/i){
					$treffer_anzahl ++;
					if ($treffer_anzahl > 20){
						print "weitere Treffer anzeigen? (J / n)";	# ask for more words after 20 hits
						$e = <STDIN>;
						last SUCHE if ($e =~ /n/i);
						$treffer_anzahl = 0;
					}
					treffer_drucken($_) 
				}
			}
		}
	}
	
}

# print the findings
sub treffer_drucken{
	($erste_spalte = $_) =~ s/($was_finden)/\e[4m$1\e[0m/gi;
	$treffer{$_} =~  s/($was_finden)/\e[4m$1\e[0m/gi;
	print $erste_spalte, " ", "-"x($laengstes - length($_)), " ", $treffer{$_}, "\n" ;
}
