import { senhaOk } from './_auth.js';

export default function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (!process.env.ADMIN_PASSWORD) return res.status(500).json({ ok: false, error: 'ADMIN_PASSWORD não configurada na Vercel' });
  const ok = senhaOk(req.headers['x-pass']);
  res.status(ok ? 200 : 401).json({ ok, blob: true });
}
