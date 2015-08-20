#!/usr/bin/env ruby
# encoding: utf-8

%w{open-uri nokogiri}.each { |l| require l; }
require_relative '../../converter/ruby/database.rb'

ROOT_URL = "http://www.vsvo.si/images/pdf/"
OUTPUT_DIR = ENV["UNIVIZOR_ENV"]=='development' ? './' : '/mnt/univizor/download/vsvo/'

pairs = Nokogiri::HTML(open(ROOT_URL)).xpath("//a").select {|a| a.content =~ /^.+diplomsk[oa].+\.pdf$/i }.map do |a|
  timestamp, *url = *a["href"].split("_")
  [Integer(timestamp[0,4]), ROOT_URL + a["href"]]
end

pairs.each do |year, url|
  diploma = Diploma.find_or_initialize_by(url: url) do |d|
    d.leto = year
    d.filename = ''
    d.fakulteta = 'Visoka šola za varstvo okolja (VŠVO)'
  end

  diploma.save

  filename = OUTPUT_DIR + diploma.id.to_s + ".pdf"
  diploma.update({filename: filename})

  if !File.exist?(filename)
    simple_name = url.split("/pdf/").last
    puts "Getting #{simple_name} #{diploma.id} to #{filename}."
    File.write(filename, open(url).read)
  end

  sleep 1
end
