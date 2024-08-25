from openai import OpenAI
from app.models.utils.access import access_key as key

client = OpenAI(api_key=key().openai)


class T2I_Module:
  def predict(self, prompt_text:list):
    # full_prompt = '. '.join(prompt_text)
    image_urls = []
    for i, prompt in enumerate(prompt_text):
      print(f'generating... {i+1}th/{len(prompt_text)} image')
      response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        
      )

      image_url = response.data[0].url
      image_urls.append(image_url)
    return image_urls


if __name__ == "__main__":

  T2I = T2I_Module()

  prompt_text = ["a painting of a red apple", "a painting of a blue apple"]
  image_url = T2I.predict(prompt_text)
  print(image_url)