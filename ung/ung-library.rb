require 'nokogiri'
require 'open-uri'
require_relative '../../converter/ruby/database.rb'

DIRS = ['http://www.ung.si/~library/diplome/', 'http://www.ung.si/~library/doktorati/', 'http://www.ung.si/~library/magisterij/']
OUTPUT_DIR = '/mnt/univizor/download/UNG/'

pdf_urls = []

DIRS.each do |dir|
  page = open(dir)
  Nokogiri.XML(page).search('a').each do |link|
    if link.attributes['href'] && link.attributes['href'].text[-1] == '/' && link.attributes['href'].text != '/~library/'
      subdir = dir + link.attributes['href'].text
      # puts subdir
      subpage = open(subdir)
      Nokogiri.XML(subpage).search('a').each do |sublink|
        # puts sublink
        if sublink.attributes['href'] && sublink.attributes['href'].text =~ /\.pdf$/
          pdf_urls << subdir + sublink.attributes['href'].text
        end
      end
    end
  end
end

pdf_urls.each do |url|
  filename = OUTPUT_DIR + url.split("/")[-1]
  puts "Processing #{url}"
  
  # insert into db (or update)
  diploma = Diploma.find_by(url: url) || Diploma.new
  diploma.url = url
  diploma.filename = OUTPUT_DIR + diploma.id.to_s + ".pdf"
  diploma.naslov = ''
  diploma.fakulteta = ''
  diploma.leto = ''
  diploma.data = ''
  diploma.avtor = ''
  diploma.save

  # change filename
  id_filename = OUTPUT_DIR + "#{diploma.id}.pdf"

  # temporary, we don't want to redownload files
  if File.exist?(filename) && !File.exist?(id_filename)
    puts "Renaming #{filename} -> #{id_filename}"
    File.rename(filename, id_filename)
  end

  # save to disk
  if File.exist?(id_filename)
    puts "SKIP writing #{id_filename}"
  else
    puts "writing #{id_filename}"
    File.write(id_filename, open(url).read)
  end
end

