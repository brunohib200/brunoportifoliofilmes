import { list, put } from '@vercel/blob';
import { senhaOk } from './_auth.js';

const PATH = 'site/config.json';

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method === 'GET') {
    const { blobs } = await list({ prefix: PATH });
    const b = blobs.find(x => x.pathname === PATH);
    if (!b) return res.status(404).json({ error: 'sem config salva ainda' });
    const r = await fetch(b.url + '?t=' + Date.now(), { cache: 'no-store' });
    return res.status(200).json(await r.json());
  }

  if (req.method === 'POST') {
    if (!senhaOk(req.headers['x-pass'])) return res.status(401).json({ error: 'senha incorreta' });
    let data = req.body;
    if (typeof data === 'string') {
      try { data = JSON.parse(data); } catch (e) { data = null; }
    }
    if (!data || typeof data !== 'object') return res.status(400).json({ error: 'json inválido' });
    try {
      await put(PATH, JSON.stringify(data), {
        access: 'public',
        contentType: 'application/json',
        addRandomSuffix: false,
        allowOverwrite: true,
        cacheControlMaxAge: 60,
      });
    } catch (e) {
      return res.status(500).json({ error: 'falha ao gravar: ' + e.message });
    }
    return res.status(200).json({ ok: true });
  }

  res.status(405).json({ error: 'método inválido' });
}
