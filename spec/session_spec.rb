require_relative '../lib/flickr-to-go/session'
require_relative '../lib/flickr-to-go/console_auth_ui_adapter'
require 'flickraw'

describe 'Session' do
	let(:flickr_client) { instance_double(FlickRaw::Flickr) }
	let(:auth_adapter) { instance_double(FlickrToGo::ConsoleAuthUiAdapter) }
	let(:subject) { FlickrToGo::Session.new(flickr_client, auth_adapter) }

	describe '#authorize' do
		context 'When the session is already authorized' do
			before do
				subject.access_token = 'at'
				subject.access_secret = 'as'
			end

			it 'should do nothing' do
				expect(subject.authorize).to eq(true)
			end
		end

		context 'When the session is not already authorized' do
			let(:oauth_token) do
				{ 'oauth_token' => 't', 'oauth_token_secret' => 's' } 
			end
			let(:url) { "the auth URL" }
			let(:access_token) { 'at' }
			let(:access_secret) { 'as' }

			before do
				expect(flickr_client).to receive(:get_request_token)
					.and_return(oauth_token)
				expect(flickr_client).to receive(:get_authorize_url).with('t')
					.and_return(url)
			end
	
			context 'When an access code is provided' do
				let(:code) { '1234-45-678' }
	
				before do
					expect(auth_adapter).to receive(:request_access_code).with(url)
						.and_return(code)
				end
	
				it 'requests and stores an access token' do
					expect(flickr_client).to receive(:get_access_token)
						.with('t', 's', code)
					expect(flickr_client).to receive(:access_token)
						.and_return(access_token)
					expect(flickr_client).to receive(:access_secret)
						.and_return(access_secret)
	
					expect(subject.authorize).to eq(true)
	
					expect(subject.access_token).to eq(access_token)
					expect(subject.access_secret).to eq(access_secret)
				end
			end
	
			context 'When an access code is not provided' do
				before do
					expect(auth_adapter).to receive(:request_access_code).with(url)
						.and_return(nil)
				end
	
				it 'returns falsy' do
					expect(subject.authorize).to be_falsy
				end
			end
		end
	end
end
