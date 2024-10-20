# High-Level Flow


* User Data Collection: The user_data_service collects or receives data about the user, like personal details or preferences. It stores this data in a PostgreSQL database.
* Claude API Integration: The claude_integration_service listens to RabbitMQ for new user data, then sends it to the Claude API for processing. It receives the response with dashboard suggestions.
* YAML Generation: The yaml_generation_service takes the Claude API's output and creates a YAML configuration file, which will later be used for dashboard creation.
* Dashboard Creation: The dashboard_creation_service reads the generated YAML file and communicates with the Metabase API to create a dashboard using this configuration.