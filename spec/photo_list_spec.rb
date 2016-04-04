require_relative '../lib/flickr-to-go/photo_list'
require_relative 'mock_session'
require 'json'


describe 'PhotoList' do
  let(:session) { MockSession.new(instance_double(FlickRaw::Flickr)) }
  let(:path) { 'photos.json' }

  describe '.download' do
    it 'should download pages until one is empty' do
      photos = [
        {"id"=>"25461030990","owner"=>"21041082@N02","secret"=>"x",
          "server"=>"1521","farm"=>2,"title"=>"","ispublic"=>1,
          "isfriend"=>0, "isfamily"=>0},
        {"id"=>"24420214365","owner"=>"21041082@N02","secret"=>"x",
          "server"=>"1704","farm"=>2,"title"=>"15th & Leary",
          "ispublic"=>1,"isfriend"=>0,"isfamily"=>0 },
        {"id"=>"23793491473","owner"=>"21041082@N02","secret"=>"y",
          "server"=>"1514","farm"=>2,"title"=>"Occidental and Jackson",
          "ispublic"=>1,"isfriend"=>0,"isfamily"=>0}
      ]
      page_size = 2
      expect(session).to receive(:get_user_photos)
        .with(1, page_size, 3, :original_format)
        .and_return([photos[0], photos[1]])
      expect(session).to receive(:get_user_photos)
        .with(2, page_size, 3, :original_format)
        .and_return([photos[2]])
      expect(File).to receive(:write).with(path, anything) do |p, s|
        expect(JSON.parse(s)).to eq(photos)
      end
      result = FlickrToGo::PhotoList.download(session, page_size)
      expect(result).to eq(photos)
    end
  end
end
