import openai 
import streamlit as st 

class open_ai:

    class ClientConnectionError(Exception):
        pass
    
    class VendorConnectionError(Exception):
        pass

    class ClientCredentialError(Exception):
        pass 

    class ClientRateLimitError(Exception):
        pass

    class ClientRequestError(Exception):
        pass

    def __init__(self, api_key, restart_sequence, stop_sequence):
        self.api_key = api_key
        openai.api_key = api_key 
        self.stop_sequence = stop_sequence
        self.restart_sequence = restart_sequence

    # generic function to invoke openai calls 
    def _invoke_call(self, call_string):
        try:
            result = eval(f"{call_string}")
            return result      

        except openai.error.Timeout as e:
            raise self.ClientConnectionError("Request timeout. Retry later.")

        except openai.error.APIConnectionError as e:
            raise self.ClientConnectionError("API Connection Error. Check connection settings.")

        except openai.error.APIError as e:
            raise self.VendorConnectionError("OpenAI API issue. Retry later.")

        except openai.error.ServiceUnavailableError as e:
            raise self.VendorConnectionError("OpenAI service issue. Retry later.")

        except openai.error.PermissionError as e:
            raise self.ClientCredentialError("Credential permission error. Credential does not have permission.")

        except openai.error.AuthenticationError as e:
            raise self.ClientCredentialError("Credential authentication error. API key or token was invalid, expired, or revoked.")

        except openai.error.RateLimitError as e:
            raise self.ClientRateLimitError("Rate Limit reached. Retry later")

        except openai.error.InvalidRequestError as e:
            raise self.ClientRequestError("Bad requests.")

    # validate model parameters 
    def _validate_model_config(self, model_config_dict):
        required_fields = ['model', 'temperature', 'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty']

        for field in required_fields:
            if field not in model_config_dict:
                raise self.ClientRequestError("Bad model configuration request") 
        return True

    # get OpenAI models -- mainly used to validate the key  
    def get_models(self):
        try:
            return self._invoke_call("openai.Model.list()")
        except Exception as e:
            raise  
        
    # validate API key (by making a call to the get models endpoint)
    @st.cache_data(show_spinner=False, ttl=600)
    def validate_key(_self):
        try:
            models = _self.get_models()
            return True
        except:
            return False 

    # main call to get bot response 
    @st.cache_data(show_spinner=False, ttl=30)
    def get_completion(_self, model_config_dict, message):
        model_config_validated = _self._validate_model_config(model_config_dict)
        #key_validated = self.validate_key()
        key_validated = 1

        if model_config_validated and key_validated:
            get_completion_call_string = (
            """openai.Completion.create(
                model="{0}",
                prompt="{1}",
                temperature={2},
                max_tokens={3},
                top_p={4},
                frequency_penalty={5},
                presence_penalty={6},
                stop=['{7}']
                )""").format(
                    model_config_dict['model'],
                    message.replace("\"","'"),
                    model_config_dict['temperature'],
                    model_config_dict['max_tokens'],
                    model_config_dict['top_p'],
                    model_config_dict['frequency_penalty'],
                    model_config_dict['presence_penalty'],
                    _self.stop_sequence
                )            
            
            try:
                completions = _self._invoke_call(get_completion_call_string)
                return completions
            except Exception as e:
                raise 
        else:
            if not model_config_validated:
                raise _self.ClientRequestError("Bad Requests. model_config_dict missing required fields")
            if not key_validated:
                raise _self.ClientCredentialError("Credential authentication error. API key or token was invalid, expired, or revoked.")


    # call to get moderation 
    def get_moderation(self, user_message):
        #key_validated = self.validate_key()
        key_validated = 1 

        if key_validated:
            get_moderation_call_string = ("""openai.Moderation.create(input="{0}")""".format(user_message))

            try:
                moderation = self._invoke_call(get_moderation_call_string)
                moderation_result = moderation['results'][0]
                flagged_categories = [category for category, value in moderation_result['categories'].items() if value]

                return {'flagged': moderation_result['flagged'], 'flagged_categories':flagged_categories}
            except Exception as e:
                raise 

# a = open_ai(api_key='',restart_sequence='|USER|', stop_sequence='|SP|')
# message = "I hate my boss and all leadership in the new company!"
# print(a.get_moderation(message))

# print(a.validate_key())
# print(a.get_models())