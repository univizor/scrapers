#!/usr/bin/perl -w

use strict;
use Unicode::Normalize;

my $home = "http://www.odun.univerza.si/";
my $search = 'Brskanje2.php?kat1=letoIzida&kat2=';
my $paging = 10;
my @years = (1999..2015);

# http://repozitorij.ung.si/Brskanje2.php?kat1=letoIzida&kat2=2015
foreach my $year (@years) {
    my $page = 1;
	my $pages = 1;
	while ($page <= $pages) {
	    if (!-f "raw/$year-$page.html") {
	        system("wget -O 'raw/$year-$page.html' '$home$search$year'");
	        sleep 1;
	    }
		my $html = readpipe("cat 'raw/$year-$page.html'");	
# <div class="Stat">1 - 10 / 17</div>
		if ($html =~ /class="Stat">.*? \/ (\d+?)</) {
			my $total = $1;
			$pages = int($total / $paging) + 1;
		}

#<tr class="Alt"><td><div class="Logo"><img src="teme/rungDev/img/logo/fh.gif" alt="Logo" title="Fakulteta za humanistiko"></div><div class="Stevilka">10.</div><div class="Besedilo"><a href="IzpisGradiva.php?id=1793&amp;lang=slv">Razvoj obrti in industrije v Sežani od konca 2. svetovne vojne do Londonskega memoranduma o soglasju leta 1954</a><br><a href="Iskanje.php?lang=slv&amp;type=napredno&amp;stl0=Avtor&amp;niz0=Martin+Garzarolli">Martin Garzarolli</a>, 2015<br><p><strong>Ključne besede:</strong> <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=diplomske+naloge&amp;lang=slv">diplomske naloge</a>, <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=Se%C5%BEana&amp;lang=slv">Sežana</a>, <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=20.+stoletje&amp;lang=slv">20. stoletje</a>, <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=industrija&amp;lang=slv">industrija</a>, <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=obrt&amp;lang=slv">obrt</a>, <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=centralnoplansko+gospodarstvo&amp;lang=slv">centralnoplansko gospodarstvo</a><br><strong>Objavljeno:</strong> 27.02.2015; <strong>Ogledov:</strong> 161; <strong>Prenosov:</strong> 4<br><a href="Dokument.php?id=2863&amp;lang=slv"><img src="teme/rungDev/img/fileTypes/pdf.gif" alt=".pdf" title=".pdf"></a> <a href="Dokument.php?id=2863&amp;lang=slv">Polno besedilo</a> (2,22 MB)<br>Gradivo ima več datotek! <a href="IzpisGradiva.php?id=1793&amp;lang=slv">Več...</a><br></p></div></td></tr>

# <td><div class="Logo"><img src="teme/rungDev/img/logo/fps.gif" alt="Logo" title="Fakulteta za podiplomski študij" /></div><div class="Stevilka">8.</div><div class="Besedilo"><a href="IzpisGradiva.php?id=1795&lang=slv">Environmental stability and toxicity assessment of chlorantraniliprole and its derivatives</a><br/><a href="Iskanje.php?lang=slv&type=napredno&amp;stl0=Avtor&amp;niz0=Vesna+Lavti%C5%BEar">Vesna Lavtižar</a>, 2015<br/><p><strong>Objavljeno:</strong> 05.03.2015; <strong>Ogledov:</strong> 140; <strong>Prenosov:</strong> 3<br /><a href="Dokument.php?id=2867&lang=slv"><img src="teme/rungDev/img/fileTypes/pdf.gif" alt=".pdf" title=".pdf" /></a> <a href="Dokument.php?id=2867&lang=slv">Polno besedilo</a> (2,75 MB)<br />Gradivo ima več datotek! <a href="IzpisGradiva.php?id=1795&lang=slv">Več...</a><br/></p></div></td> at scrape.pl line 31.

# <div class="Besedilo"><a href="IzpisGradiva.php?id=1795&lang=slv">Environmental stability and toxicity assessment of chlorantraniliprole and its derivatives</a><br/><a href="Iskanje.php?lang...">Vesna Lavtižar</a>, 2015<br/><p><strong>Objavljeno:</strong> 05.03.2015; <strong>Ogledov:</strong> 140; <strong>Prenosov:</strong> 3<br /><a href="Dokument.php?id=2867&lang=slv">

# <tr><td><div class="Logo"><img src="teme/rungDev/img/logo/razno.gif" alt="Logo" title="Univerza v Novi Gorici" /></div><div class="Stevilka">1.</div><div class="Besedilo"><a href="IzpisGradiva.php?id=1719&lang=slv">Video-integrirani mediji</a><br/><a href="Iskanje.php?lang=slv&type=napredno&amp;stl0=Avtor&amp;niz0=Ale%C5%A1+Vaupoti%C4%8D">Aleš Vaupotič</a>, <a href="Iskanje.php?lang=slv&type=napredno&amp;stl0=Avtor&amp;niz0=Narvika+Bovcon">Narvika Bovcon</a>, 2002<br/><p><strong>Ključne besede:</strong> <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=video&lang=slv">video</a>, <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=instalacija&lang=slv">instalacija</a>, <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=novi+mediji&lang=slv">novi mediji</a>, <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=&lang=slv"></a><br/><strong>Objavljeno:</strong> 22.01.2015; <strong>Ogledov:</strong> 116; <strong>Prenosov:</strong> 0<br /><a href="Dokument.php?id=1734&lang=slv"><img src="teme/rungDev/img/fileTypes/html.gif" alt="URL" title="URL" /></a> <a href="Dokument.php?id=1734&lang=slv">Polno besedilo</a></p></div></td></tr>

# <tr class="Alt"><td><div class="Logo"><img src="teme/rungDev/img/logo/razno.gif" alt="Logo" title="Univerza v Novi Gorici" /></div><div class="Stevilka">2.</div><div class="Besedilo"><a href="IzpisGradiva.php?id=1249&lang=slv">The FLUKA code</a><br/><a href="Iskanje.php?lang=slv&type=napredno&amp;stl0=Avtor&amp;niz0=A.+Fass%C3%B2">A. Fassò</a>, <a href="Iskanje.php?lang=slv&type=napredno&amp;stl0=Avtor&amp;niz0=Maria+Vittoria+Garzelli">Maria Vittoria Garzelli</a>, 2003<br/><p><strong>Ključne besede:</strong> <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=FLUKA&lang=slv">FLUKA</a>, <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=hadroni&lang=slv">hadroni</a>, <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=interakcije&lang=slv">interakcije</a>, <a href="Iskanje.php?type=napredno&amp;stl0=KljucneBesede&amp;niz0=&lang=slv"></a><br/><strong>Objavljeno:</strong> 15.10.2013; <strong>Ogledov:</strong> 331; <strong>Prenosov:</strong> 0<br /><a href="Dokument.php?id=1249&lang=slv"><img src="teme/rungDev/img/fileTypes/html.gif" alt="URL" title="URL" /></a> <a href="Dokument.php?id=1249&lang=slv">Polno besedilo</a></p></div></td></tr>

		while ($html =~ /<tr.*?>(.*)<\/tr>/g) {
			my $row = $1;
			#$row =~ s/<a href=\"Iskanje.php\?.*?\">//g;
			if ($row =~ /<div class=\"Besedilo\"><a .*?>(.*?)<\/a><.*?\">(.*?)<\/a>, (\d+)<br.*>.*?<a href=\"(Dokument.php.*?)\">Polno besedilo/) {

				my $title = $1;
				my $author = $2;
					$author =~ s/<.*?>//g;
				my $year = $3;
				my $document = $4;
				my $detailsurl;

				if (!$year or !$author or !$document) { warn 'blo'; next; }

				print "$title\t$author\t$year\t$home$document\n";

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
