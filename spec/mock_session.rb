class MockSession
  def initialize(flickr_client)
    @flickr = flickr_client
    @auth_result = true
  end

  def authorize
    @auth_result
  end

  def get_user_photos(page, per_page, safe_search)
  end

  attr_accessor(:flickr)
  attr_accessor(:auth_result)
end
