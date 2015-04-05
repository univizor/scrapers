require 'open-uri'
require 'nokogiri'
require 'rest-client'

url_root = "http://repozitorij.ung.si/"
start_url = "http://repozitorij.ung.si/Brskanje2.php?kat1=jezik&kat2=1060"
output_dir = "/mnt/univizor/download/UNG/"

url = start_url

while true
  result = open(url)
  list_doc = Nokogiri.XML(result)

  links = list_doc.search('a').map { |node| node.attributes['href'].to_s if node.text =~ /Polno besedilo/ }.compact
  # "Dokument.php?id=2881&lang=slv"

  links_fixed = links.map{|l| url_root + l.gsub('=slv', '&lang=slv')}
  # "http://repozitorij.ung.si/Dokument.php?id=2881&lang=slv"

  links_fixed.each do |link|
    puts link
    result = open(link)
    filename = link.match(/id=(\d+)/)[1] + ".pdf"
    x = Nokogiri.XML(result).search('input')
    key = nil
    x.each do |node|
      # puts node
      if node.attributes['name'] && node.attributes['name'].text == 'key'
        # puts node
        key = node.attributes['value'].text
        break
      end
    end
   
    if File.exist?(output_dir + filename)
      next
    end

    begin
      if key
        link_post = link.gsub('&lang=slv', '')
        cookies = result.meta['set-cookie'].split('; ',2)[0].split("=")
        doc = RestClient.post link_post, { key: key }, cookies: { cookies[0] => cookies[1] }
        File.write(output_dir + filename, doc)
      end
    rescue Exception => e
      puts "skipping link #{link_post}, #{e}"
    end
  end

  begin
    link_to_next = list_doc.search('a').select { |node| node.inner_html =~ /Na naslednjo stran/ }[0].attributes['href'].text
    url = url_root + link_to_next
  rescue
    puts "next page not found"
    break
  end

  puts "new page: #{link_to_next}"
end

