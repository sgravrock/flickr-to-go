module FlickrToGo
	class ConsoleAuthUiAdapter
		def request_access_code(auth_url)
			if system('open', auth_url)
				puts 'The Flickr login page should have opened in your browser. Please log in.'
			else
				puts 'Open this URL in your browser to log in to Flickr:'
				puts auth_url
			end
			
			puts 'When you have finished logging in, please enter the access code here:'
			gets.strip
		end
	end
end
