module FlickrToGo
	class Session
		def initialize(flickr_client, auth_ui_adapter)
			@flickr = flickr_client
			@auth_ui_adapter = auth_ui_adapter
		end

		def authorize
			return true if access_token && access_secret
			token = @flickr.get_request_token
			code = get_access_code(token)
			redeem_access_code(token, code) if code
		end

		attr_accessor(:access_token, :access_secret)

		private

		def get_access_code(oauth_token)
			url = @flickr.get_authorize_url(oauth_token['oauth_token'])
			code = @auth_ui_adapter.request_access_code(url)
		end

		def redeem_access_code(oauth_token, access_code)
			@flickr.get_access_token(oauth_token['oauth_token'],
				oauth_token['oauth_token_secret'], access_code)
			self.access_token = @flickr.access_token
			self.access_secret = @flickr.access_secret
			true
		end

		def flickr
			raise 'Use @flickr, not the global flickr variable'
		end
	end
end
