import { timingSafeEqual } from 'node:crypto';

export function senhaOk(given) {
  const pass = process.env.ADMIN_PASSWORD || '';
  const a = Buffer.from(String(given || ''));
  const b = Buffer.from(pass);
  return pass !== '' && a.length === b.length && timingSafeEqual(a, b);
}
