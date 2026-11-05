import type {NextConfig} from 'next';
const config:NextConfig={
  poweredByHeader:false,
  async headers(){return [{source:'/:path*',headers:[
    {key:'X-Content-Type-Options',value:'nosniff'},
    // Native same-origin POST forms need their Origin for the CSRF check.
    // Still omit referrers when navigating to another origin.
    {key:'Referrer-Policy',value:'same-origin'},
    {key:'X-Frame-Options',value:'DENY'},
    {key:'Permissions-Policy',value:'camera=(), microphone=(self), geolocation=()'},
  ]}]}
};
export default config;
