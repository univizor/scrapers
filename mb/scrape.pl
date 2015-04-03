#!/usr/bin/perl -w

use strict;
use Unicode::Normalize;

my $home = "https://dk.um.si/";
my $paging = 10;

# https://dk.um.si/Brskanje.php?id=29&lang=slv&page=10
foreach my $line (readpipe("cat list.txt")) {
  chop $line;
  if ($line =~ /<a href=\"(.*?id=(\d+).*?)\">(.*?)</) {
    my $link = $1;
    my $org = $3;
    my $cat = $2;
    
    my $page = 1;
	my $pages = 1;
	while ($page <= $pages) {
	    if (!-f "raw/$cat-$page.html") {
	        system("wget -O 'raw/$cat-$page.html' '$home$link&chkZDat=on&page=$page'");
	        sleep 1;
	    }
	
		my $html = readpipe("cat 'raw/$cat-$page.html'");
	
		my $what; my $who; my $where;
# Pot: / <a href="Brskanje.php?lang=slv&id=25">Diplomska dela</a> / <b>FKBV</b> / <br/>Opis: Fakulteta za kmetijstvo in biosistemske vede<br/>  <br/>
		if ($html =~ /Pot:.*?>(.*?)<\/a> \/ <b>(.*?)<\/b> \/ <br\/>Opis\: (.*?)</s) {
			$what = $1;
			$who = $2;
			$where = $3;
		}
		if ($html =~ /class="Stat">.*? \/ (\d+?)</) {
			my $total = $1;
			$pages = int($total / $paging) + 1;
		}

# <tr class="Alt"><td><div class="Logo"><img src="teme/dkumDev2/img/logo/FK_logo.gif" alt="Logo" title="Fakulteta za kmetijstvo in biosistemske vede" /></div><div class="Stevilka">2.</div><div class="Besedilo"><a href="IzpisGradiva.php?id=9570&lang=slv">Učinkovitost bakrovih pripravkov za preprečevanje okužb jablan z bakterijo Erwinia amylovora Burr. v poletnem času : diplomsko delo</a><br/><a href="Iskanje.php?hidType=napredno&amp;ddlStolpec0=Avtor&amp;txtNiz0=Sandi+%C5%BDiher&lang=slv">Sandi Žiher</a>, 2008<br/><p><strong>Ključne besede:</strong> <a href="Iskanje.php?hidType=napredno&amp;ddlStolpec0=KljucneBesede&amp;txtNiz0=Erwinia+amylovora&lang=slv">Erwinia amylovora</a>, <a href="Iskanje.php?hidType=napredno&amp;ddlStolpec0=KljucneBesede&amp;txtNiz0=jablana&lang=slv">jablana</a>, <a href="Iskanje.php?hidType=napredno&amp;ddlStolpec0=KljucneBesede&amp;txtNiz0=hru%C5%A1ev+o%C5%BEig&lang=slv">hrušev ožig</a>, <a href="Iskanje.php?hidType=napredno&amp;ddlStolpec0=KljucneBesede&amp;txtNiz0=zatiranje+bolezni&lang=slv">zatiranje bolezni</a>, <a href="Iskanje.php?hidType=napredno&amp;ddlStolpec0=KljucneBesede&amp;txtNiz0=bakrovi+fungicidi&lang=slv">bakrovi fungicidi</a><br/><strong>Objavljeno:</strong> 19.01.2009; <strong>Ogledov:</strong> 1690; <strong>Prenosov:</strong> 111<br/><a href="Dokument.php?id=7008&langslv"><img src="teme/dkumDev2/img/fileTypes/pdf.gif" alt=".pdf" title=".pdf" /></a> <a href="Dokument.php?id=7008"> Polno besedilo</a> (1,78 MB)</p></div></td></tr>

		while ($html =~ /<tr.*?>(.*)<\/tr>/g) {
			my $row = $1;

			if ($row =~ /<div class="Besedilo"><a .*?>(.*?)<\/a><br\/>.*?>(.*?)<\/a>, (\d+)<.*?><a href="(Dokument.php.*?)">/) {
				my $author = $2;
				my $year = $3;
				my $document = $4;
				my $title = $1;
				my $detailsurl;
				print "$what\t$who\t$where\t$title\t$author\t$year\t$home$document\n";

				my $slug = &slugify("$author-$year");
				if (!-f "docs/$slug.pdf") {
# 1. fetch the tos page and store the cookie
					system("curl -s -D lccookie '$home$document' > temp.html");
					my $interstitial = readpipe("cat temp.html");
					my $key = &get_key($interstitial);
					warn $key;
# 2. fetch the document using the cookie
					system("curl -L -s -b lccookie -d 'key=$key' '$home$document' > 'docs/$slug.pdf'") if $key;
					sleep 1;
				}
			} else { warn 'bla'; }
		}

		$page++;
	}
  } #else { warn 'bla'; }
}

sub get_key {
	my ($html) = @_;
	if ($html =~ /<input type\=\"hidden\" name=\"key\" value=\"(.*?)\" \/>/s) {
		return $1;
	} else { return 'blu'; }
}

sub slugify {
    my ($input) = @_;

    $input = NFKD($input);         # Normalize the Unicode string
    $input =~ tr/\000-\177//cd;    # Strip non-ASCII characters (>127)
    $input =~ s/[^\w\s-]//g;       # Remove all characters that are not word characters (includes _), spaces, or hyphens
    $input =~ s/^\s+|\s+$//g;      # Trim whitespace from both ends
    $input = lc($input);
    $input =~ s/[-\s]+/-/g;        # Replace all occurrences of spaces and hyphens with a single hyphen

    return $input;
}
