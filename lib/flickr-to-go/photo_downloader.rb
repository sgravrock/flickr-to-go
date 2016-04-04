require 'FlickRaw'
require 'ostruct'
require 'net/http'

module FlickrToGo
	class PhotoDownloader
    def initialize(http_client = nil)
      @http_client = http_client || Net::HTTP
    end

		def download_originals(photo_list)
      photo_list.each do |photo|
        url = FlickRaw.url_o(OpenStruct.new(photo))
        puts "==== #{url} ===="
        response = @http_client.get(url, {})
        filename = File.join('originals', File.basename(url))
        File.open(filename, 'wb') { |f| f.write(response.body) }
      end
		end
	end
end
