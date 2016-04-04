require_relative '../lib/flickr-to-go/cli'
require_relative '../lib/flickr-to-go/photo_downloader'
require_relative 'mock_session'
require 'json'

class ExitedError < StandardError
end

describe 'Cli' do
  let(:session) { MockSession.new(instance_double(FlickRaw::Flickr)) }
  let(:photo_downloader) { instance_double(FlickrToGo::PhotoDownloader) }
  let(:subject) do
    s = FlickrToGo::Cli.new(session, photo_downloader)
    allow(s).to receive(:exit) { raise ExitedError }
    s
  end

  describe '#run' do
    before do
      allow(FlickrToGo::PhotoList).to receive(:download)
      allow(photo_downloader).to receive(:download_originals)
    end

    context 'When authorization fails' do
      it 'should exit' do
        session.auth_result = false
        expect { subject.run }.to raise_error(ExitedError)
      end
    end

    it 'should download the list of photos' do
      expect(FlickrToGo::PhotoList).to receive(:download).with(session)
      subject.run
    end

    it 'should download the originals' do
      expect(photo_downloader).to receive(:download_originals)
      subject.run
    end
  end
end
