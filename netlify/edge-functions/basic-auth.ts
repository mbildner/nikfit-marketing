// HTTP Basic Auth gate for pre-launch private review.
// No-op unless BASIC_AUTH_USER and BASIC_AUTH_PASSWORD are both set:
//   netlify env:set BASIC_AUTH_USER nikki
//   netlify env:set BASIC_AUTH_PASSWORD <something>
// To remove the gate before launch, unset both vars (or just delete this file).

// Constant-time string comparison. Pads to the longer length so the loop
// runs the same number of iterations regardless of where a mismatch occurs,
// preventing observable timing differences from leaking secret bytes.
function timingSafeEqual(a: string, b: string): boolean {
  const len = Math.max(a.length, b.length);
  let diff = a.length ^ b.length;
  for (let i = 0; i < len; i++) {
    diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  }
  return diff === 0;
}

export default async (req: Request): Promise<Response | void> => {
  const user = Netlify.env.get("BASIC_AUTH_USER");
  const pass = Netlify.env.get("BASIC_AUTH_PASSWORD");
  if (!user || !pass) return;

  const provided = req.headers.get("authorization") ?? "";
  const expected = "Basic " + btoa(`${user}:${pass}`);
  if (timingSafeEqual(provided, expected)) return;

  return new Response("Authentication required.", {
    status: 401,
    headers: {
      "WWW-Authenticate": 'Basic realm="nikfit"',
      "Cache-Control": "no-store",
    },
  });
};

export const config = { path: "/*" };
