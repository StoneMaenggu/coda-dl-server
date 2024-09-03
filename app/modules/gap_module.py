from openai import OpenAI
from app.models.utils.access import access_key as key
#from access import access_key as key

client = OpenAI(api_key=key().openai)

class GAP_Module:
  def predict(self, prompt_text:list):
    gap_response = client.chat.completions.create(
    model="gpt-4",
    messages=[
      {
        "role": "system",
        "content": '''
        You will be provided with list of korean words, and your task is to make it clean.
        There should be no duplication within a sentence and there should be no semantic change.
        If it doesn't make sense, you can delete some words.
        Example of this task:
        input: ["축구 축구 친구 친구 친구 친구 밥 친구 친구 축구", "축구 축구 얻다 얻다 얻다 2점 얻다 2점 축구", "친구 친구 친구 축하 축하 축하 축하 받다 가다 받다 가다", "뛰다 깊다 깊다 잠 잠 잠 잠"]
        output: ["축구 친구", "축구 얻다 2점", "친구 축하 받다", "깊다 잠"]
        '''
      },
      {
        "role": "user",
        "content": f"{prompt_text}"
      }
    ],
    temperature=0.7,
    top_p=1)

    gaped_response = gap_response.choices[0].message.content
    print(f"gaped Prompt: {gaped_response}")

    return gaped_response


if __name__ == "__main__":

  GAP = GAP_Module()

  prompt_text = ["날씨 가다 날씨 날씨 덥다 덥다 덥다 화 화 화 기분 화", "자다 목 목 목 목 마르다 마르다 마르다 물 물 물  물 마시다 마시다", "수영장 하늘 수영장 수영장 가다 가다 놀다 가다 놀다", "재미 재미 즐겁다 비 비 있다 있다 있다 잠 잠 잠 피곤하다 잠"]
  gap_result = GAP.predict(prompt_text)
  print(gap_result)