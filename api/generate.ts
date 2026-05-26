import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // CORSの設定 (モバイルアプリやExpo Goからのリクエストを制限なく許可する)
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  // OPTIONSリクエスト（CORSプリフライト）には200 OKで即座に応答
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { prompt, imageBase64 } = req.body;
  if (!prompt || !imageBase64) {
    res.status(400).json({ error: 'Missing prompt or imageBase64🐾' });
    return;
  }

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    res.status(500).json({ error: 'サーバーに GEMINI_API_KEY が設定されていません。Vercelの環境変数をご確認ください🐾' });
    return;
  }

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                { text: prompt },
                {
                  inlineData: {
                    mimeType: 'image/jpeg',
                    data: imageBase64,
                  },
                },
              ],
            },
          ],
          generationConfig: {
            responseMimeType: 'application/json',
          },
        }),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      res.status(response.status).json({ error: `Gemini API Error: ${errorText}` });
      return;
    }

    const resData = await response.json();
    res.status(200).json(resData);
  } catch (error: any) {
    console.error(error);
    res.status(500).json({ error: error.message || '内部エラーが発生しました🐾' });
  }
}
