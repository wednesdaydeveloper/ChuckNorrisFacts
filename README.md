# ChuckNorrisFactsBot for LINE

gcloud config set project [PROJECT_ID]

gcloud functions deploy chuckNorrisFacts --trigger-http --runtime=python38 --env-vars-file .env.yaml