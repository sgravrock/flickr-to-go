require_relative 'session'
require_relative 'photo_list'

module FlickrToGo
  class Cli
    def self.run
      session = Session.with_app_credentials(require_env('FLICKR_API_KEY'),
        require_env('FLICKR_API_SECRET'))
      new(session).run
    end

    def initialize(session)
      @session = session
    end

    def run
      exit(1) unless @session.authorize
      PhotoList.download(@session)
    end

    class << self
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
end
