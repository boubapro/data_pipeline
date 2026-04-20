.PHONY: install setup-aws setup-keys setup deploy run test

install:
	curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
	unzip -q /tmp/awscliv2.zip -d /tmp/awscli
	sudo /tmp/awscli/aws/install --update
	rm -rf /tmp/awscliv2.zip /tmp/awscli
	wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --batch --yes --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
	echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $$(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
	sudo apt-get update -qq && sudo apt-get install -y terraform
	pip install dbt-snowflake
	@echo "✅ Tout est installé"

setup-aws:
	aws configure set aws_access_key_id $$AWS_ACCESS_KEY_ID
	aws configure set aws_secret_access_key $$AWS_SECRET_ACCESS_KEY
	aws configure set default.region $$AWS_DEFAULT_REGION
	@echo "✅ AWS configuré"

setup-keys:
	echo "$$SNOWFLAKE_PRIVATE_KEY" > /workspaces/data_pipeline/rsa_key.p8
	chmod 600 /workspaces/data_pipeline/rsa_key.p8
	@echo "✅ Clé RSA restaurée"

setup: install setup-aws setup-keys
	@echo "✅ Environnement complet prêt"

deploy:
	bash aws/deploy.sh

run:
	dbt run --select tag:every_30min

test:
	dbt test --select tag:every_30min
