require_relative 'session'
require_relative 'photo_list'
require_relative 'photo_downloader'

module FlickrToGo
  class Cli
    def initialize(session = nil, photo_downloader = nil)
      @session = session || Session.with_app_credentials(
        require_env('FLICKR_API_KEY'),
        require_env('FLICKR_API_SECRET'))
      @photo_downloader = photo_downloader || PhotoDownloader.new
    end

    def run
      exit(1) unless @session.authorize
      photo_list = PhotoList.download(@session)
      @photo_downloader.download_originals(photo_list)
    end

    private

    def require_env(name)
      value = ENV[name]

      if value.nil? || value.empty?
        $stderr.puts("Please set the #{name} environment variable.")
        exit(1)
      end

      value
    end
  end
end
