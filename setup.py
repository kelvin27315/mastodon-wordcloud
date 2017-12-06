from mastodon import Mastodon

url = "https://gensokyo.cloud"

Mastodon.create_app("wordcloud",
    api_base_url = url,
    to_file = "clientcred.secret"
    )

mastodon = Mastodon(
    client_id = "clientcred.secret",
    api_base_url = url
)

mastodon.log_in(
    "*****",
    "*****",
    to_file = "usercred.secret"
)
