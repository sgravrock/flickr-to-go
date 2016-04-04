require 'net/http'

class MockHttpClient
  def initialize
    @configs = []
    @received = []
  end

  def get(url, headers)
    config = configuration_for_url(url)
    @configs.delete(config)
    @received.push(url)
    CannedHttpResponse.create(config.response_status, config.response_headers,
      config.response_body)
  end

  attr_reader(:configs, :received)

  private

  def configuration_for_url(url)
    @configs.find { |c| c.url == url } || raise("No configuration for #{url}")
  end
end

class MockHttpConfig
  def initialize(url, response_status, response_body)
    @url = url
    @response_status = response_status
    @response_body = response_body
  end

  attr_accessor(:url, :response_status, :response_headers,
    :response_body)
end

class CannedHttpResponse < Net::HTTPResponse
  def self.create(status, headers, body)
    response = new('1.1', status, '')
    headers.each { |k, v| response[k] = v } if headers
    response.body = body
    response
  end

  attr_accessor(:body)
end

