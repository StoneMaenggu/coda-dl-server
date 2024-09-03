from openai import OpenAI
from app.models.utils.access import access_key as key
#from access import access_key as key

client = OpenAI(api_key=key().openai)

class T2I_Module:
  def predict(self, prompt_text:list):
    full_prompt = '. '.join(prompt_text)
    print(f"Full Prompt: {full_prompt}")
    translation_response = client.chat.completions.create(
    model="gpt-4",
    messages=[
      {
        "role": "system",
        "content": "You will be provided with a sentence in korean, and your task is to translate it into english and make it more descriptive. This will be 4-panel cartoon for kids."
      },
      {
        "role": "user",
        "content": f"{full_prompt}"
      }
    ],
    temperature=0.7,
    top_p=1)

    translated_prompt = translation_response.choices[0].message.content
    print(f"Translated Prompt: {translated_prompt}")

    response = client.images.generate(
      model="dall-e-3",
      prompt=f'''
        Format:
        4-panel cartoon with 2 by 2 layout.
        Do not make any frame or border between panels.

        Style:
        Drawing style painting.
        Drawing for kids.
        No text in the image.

        Contents:
        The protagonist is a 13-year-old boy, with black hair.
        He is korean.
        Story for each panel:{translated_prompt}
        All panel's story is related.
        Each panel has a different scene.

        Never make 6-panel or 9-panel drawing.
        Never make border between panels.
        ''',
      size="1024x1024",
      quality="hd",
      n=1
    )

    image_url = response.data[0].url
    # image_urls.append(image_url)
    return image_url


if __name__ == "__main__":

  T2I = T2I_Module()

  prompt_text = ["날씨 덥다 화 난다", "목 마르다 물 마시다", "수영장 가다 놀다", "재미 있다 피곤하다 잠"]
  image_url = T2I.predict(prompt_text)
  print(image_url)  