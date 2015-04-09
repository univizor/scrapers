#!/usr/bin/env ruby

%w{open-uri nokogiri}.each { |l| require l; }

def is_dev?; Dir.exists?("/Users/otobrglez"); end
def redownload?; ENV["REDOWNLOAD"] == "1"; end

ROOT_URL = "http://www.vsvo.si/images/pdf/"

doc = Nokogiri::HTML open(ROOT_URL)
urls = doc.xpath("//a").select {|a| a.content =~ /^.+diplomsk[oa].+\.pdf$/i }.map do |a|
  timestamp, *url = *a["href"].split("_")
  [timestamp, ROOT_URL + url.join("_")]
end


puts urls.inspect
