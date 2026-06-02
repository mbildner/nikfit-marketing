// HTTP Basic Auth gate for pre-launch private review.
// No-op unless BASIC_AUTH_USER and BASIC_AUTH_PASSWORD are both set:
//   netlify env:set BASIC_AUTH_USER nikki
//   netlify env:set BASIC_AUTH_PASSWORD <something>
// To remove the gate before launch, unset both vars (or just delete this file).

export default async (req: Request): Promise<Response | void> => {
  const user = Netlify.env.get("BASIC_AUTH_USER");
  const pass = Netlify.env.get("BASIC_AUTH_PASSWORD");
  if (!user || !pass) return;

  const provided = req.headers.get("authorization") ?? "";
  const expected = "Basic " + btoa(`${user}:${pass}`);
  if (provided === expected) return;

  return new Response("Authentication required.", {
    status: 401,
    headers: {
      "WWW-Authenticate": 'Basic realm="nikfit"',
      "Cache-Control": "no-store",
    },
  });
};

export const config = { path: "/*" };
