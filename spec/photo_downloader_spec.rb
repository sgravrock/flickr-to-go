require_relative '../lib/flickr-to-go/photo_downloader'
require_relative 'mock_session'
require_relative 'mock_http_client'
require 'json'

describe 'PhotoDownloader' do
	let(:session) { MockSession.new(instance_double(FlickRaw::Flickr)) }
	let(:path) { 'photos.json' }
  let(:http) { MockHttpClient.new }
  let(:subject) { FlickrToGo::PhotoDownloader.new(http) }

	describe '.download_originals' do
    let(:photo_list) do
      [
        {"id"=>"25461030990","owner"=>"21041082@N02","secret"=>"x",
          "server"=>"1521","farm"=>2,"title"=>"","ispublic"=>1,
          "isfriend"=>0, "isfamily"=>0, "originalsecret"=> "y",
          "originalformat"=>"png"
        },
        {"id"=>"24420214365","owner"=>"21041082@N02","secret"=>"x",
          "server"=>"2485","farm"=>3,"title"=>"15th & Leary",
          "ispublic"=>1,"isfriend"=>0,"isfamily"=>0, "originalsecret"=> "z",
          "originalformat"=>"jpg"
        }
      ]
    end

    it 'should download the photos' do
      urls = [
        "https://farm2.staticflickr.com/1521/25461030990_y_o.png",
        "https://farm3.staticflickr.com/2485/24420214365_z_o.jpg"
      ]
      http.configs.push(MockHttpConfig.new(urls[0], 200, 'body 1'))
      http.configs.push(MockHttpConfig.new(urls[1], 200, 'body 2'))

      expect(File).to receive(:open)
                        .with('originals/25461030990_y_o.png', 'wb') do |p, m, &block|
        f = instance_double('File')
        expect(f).to receive(:write).with('body 1')
        block.call(f)
      end

      expect(File).to receive(:open)
                        .with('originals/24420214365_z_o.jpg', 'wb') do |p, m, &block|
        f = instance_double('File')
        expect(f).to receive(:write).with('body 2')
        block.call(f)
      end

      subject.download_originals(photo_list)
      expect(http.received).to eq(urls)
    end
		# FlickRaw.url_b(info) # => "https://farm3.static.flickr.com/2485/3839885270_6fb8b54e06_b.jpg"
	end
end

