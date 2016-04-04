module FlickrToGo
	module PhotoList
		def self.download(session, page_size=500)
			save(get(session, page_size))
		end

		class << self
			private

			def get(session, page_size)
				photos = []
				i = 1
	
				loop do
					page = session.get_user_photos(i, page_size, 3, :original_format)
					photos += page
					break if page.length < page_size
					i += 1
				end
	
				photos
			end
	
			def save(photos)
				File.write('photos.json', JSON.pretty_generate(photos))
			end
		end
	end
end
