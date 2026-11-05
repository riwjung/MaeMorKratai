import {test} from 'node:test';
import assert from 'node:assert/strict';
import {sameOrigin} from '../lib/origin';
test('CSRF validates actual host, allows loopback development, rejects hostile/null origins',()=>{
 const check=(host:string,origin:string)=>sameOrigin(new Request('http://localhost:3012/api/workshop',{headers:{host,origin}}));
 assert.equal(check('127.0.0.1:3012','http://127.0.0.1:3012'),true);
 assert.equal(check('workshop.example','https://workshop.example'),true);
 for(const origin of ['https://evil.example','null','https://workshop.example.evil.example','https://workshop.example/path','http://workshop.example','https://workshop.example:444'])
  assert.equal(check('workshop.example',origin),false);
 assert.equal(sameOrigin(new Request('http://localhost:3012')),false);
});
