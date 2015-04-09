require 'open-uri'
require 'nokogiri'
require 'rest-client'
require_relative '../../converter/ruby/database.rb'

OUTPUT_DIR = '/mnt/univizor/download/gea/'

url_root = "http://gea.gea-college.si/diplome/diplomska_dela_vsp_2009.aspx?studij=1"
result = open(url_root)
list_doc = Nokogiri.XML(result)
form = list_doc.search('form')[0]

params = {"__EVENTTARGET" => "", "__EVENTARGUMENT" => "", "__LASTFOCUS" => "", "Textbox1" => ""}

form.children.each do |child|
  m = child.to_s.match(/input type="hidden".*name="(.*?)".*value="(.*?)"/)
  if m
    params[m[1]] = m[2]
  end
end

list_doc.css('input').each do |node|
  params2 = params.dup
  filename = ""
  if node.attributes['name'].content =~ /^DataList1\$ctl/
    key_x = node.attributes['name'].content + ".x"
    key_y = node.attributes['name'].content + ".y"
    params2[key_x] = "1"
    params2[key_y] = "1"
    filename = node.attributes['name'].content.match(/\$(.*)\$/)[1] + ".pdf"
  else
    next
  end

  doc = RestClient.post url_root, params2

  url = "geacollege-#{filename}"

  insert into db (or update)
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

  # save to disk
  if File.exist?(id_filename)
    puts "SKIP writing #{id_filename}"
  else
    puts "writing #{id_filename}"
    File.write(id_filename, doc)
  end
  
  sleep 1
end

"""
POST /diplome/diplomska_dela_vsp_2009.aspx?studij=1 HTTP/1.1
Host: gea.gea-college.si
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:37.0) Gecko/20100101 Firefox/37.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://gea.gea-college.si/diplome/diplomska_dela_vsp_2009.aspx?studij=1
Connection: keep-alive

DataList1$ctl03$imgOdpri.x=14
DataList1$ctl03$imgOdpri.y=8
TextBox1=
__EVENTARGUMENT=
__EVENTTARGET=
__LASTFOCUS=
__VIEWSTATEENCRYPTED=
__VIEWSTATEGENERATOR=33563C16
"""