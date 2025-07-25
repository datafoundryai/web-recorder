/**
 * Bundled by jsDelivr using Rollup v2.79.2 and Terser v5.39.0.
 * Original file: /npm/@rrweb/packer@2.0.0-alpha.18/dist/packer.js
 *
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
var r = Uint8Array,
  n = Uint16Array,
  e = Uint32Array,
  t = new r([
    0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5,
    5, 5, 5, 0, 0, 0, 0,
  ]),
  a = new r([
    0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10,
    11, 11, 12, 12, 13, 13, 0, 0,
  ]),
  f = new r([16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]),
  o = function (r, t) {
    for (var a = new n(31), f = 0; f < 31; ++f) a[f] = t += 1 << r[f - 1];
    var o = new e(a[30]);
    for (f = 1; f < 30; ++f)
      for (var i = a[f]; i < a[f + 1]; ++i) o[i] = ((i - a[f]) << 5) | f;
    return [a, o];
  },
  i = o(t, 2),
  v = i[0],
  u = i[1];
(v[28] = 258), (u[258] = 28);
for (
  var l = o(a, 0), c = l[0], h = l[1], s = new n(32768), w = 0;
  w < 32768;
  ++w
) {
  var d = ((43690 & w) >>> 1) | ((21845 & w) << 1);
  (d =
    ((61680 & (d = ((52428 & d) >>> 2) | ((13107 & d) << 2))) >>> 4) |
    ((3855 & d) << 4)),
    (s[w] = (((65280 & d) >>> 8) | ((255 & d) << 8)) >>> 1);
}
var g = function (r, e, t) {
    for (var a = r.length, f = 0, o = new n(e); f < a; ++f) ++o[r[f] - 1];
    var i,
      v = new n(e);
    for (f = 0; f < e; ++f) v[f] = (v[f - 1] + o[f - 1]) << 1;
    if (t) {
      i = new n(1 << e);
      var u = 15 - e;
      for (f = 0; f < a; ++f)
        if (r[f])
          for (
            var l = (f << 4) | r[f],
              c = e - r[f],
              h = v[r[f] - 1]++ << c,
              w = h | ((1 << c) - 1);
            h <= w;
            ++h
          )
            i[s[h] >>> u] = l;
    } else
      for (i = new n(a), f = 0; f < a; ++f)
        i[f] = s[v[r[f] - 1]++] >>> (15 - r[f]);
    return i;
  },
  p = new r(288);
for (w = 0; w < 144; ++w) p[w] = 8;
for (w = 144; w < 256; ++w) p[w] = 9;
for (w = 256; w < 280; ++w) p[w] = 7;
for (w = 280; w < 288; ++w) p[w] = 8;
var m = new r(32);
for (w = 0; w < 32; ++w) m[w] = 5;
var b = g(p, 9, 0),
  y = g(p, 9, 1),
  x = g(m, 5, 0),
  M = g(m, 5, 1),
  k = function (r) {
    for (var n = r[0], e = 1; e < r.length; ++e) r[e] > n && (n = r[e]);
    return n;
  },
  C = function (r, n, e) {
    var t = (n / 8) | 0;
    return ((r[t] | (r[t + 1] << 8)) >>> (7 & n)) & e;
  },
  E = function (r, n) {
    var e = (n / 8) | 0;
    return (r[e] | (r[e + 1] << 8) | (r[e + 2] << 16)) >>> (7 & n);
  },
  O = function (r) {
    return ((r / 8) | 0) + (7 & r && 1);
  },
  S = function (t, a, f) {
    (null == f || f > t.length) && (f = t.length);
    var o = new (t instanceof n ? n : t instanceof e ? e : r)(f - a);
    return o.set(t.subarray(a, f)), o;
  },
  A = function (r, n, e) {
    e <<= 7 & n;
    var t = (n / 8) | 0;
    (r[t] |= e), (r[t + 1] |= e >>> 8);
  },
  T = function (r, n, e) {
    e <<= 7 & n;
    var t = (n / 8) | 0;
    (r[t] |= e), (r[t + 1] |= e >>> 8), (r[t + 2] |= e >>> 16);
  },
  F = function (e, t) {
    for (var a = [], f = 0; f < e.length; ++f)
      e[f] && a.push({ s: f, f: e[f] });
    var o = a.length,
      i = a.slice();
    if (!o) return [new r(0), 0];
    if (1 == o) {
      var v = new r(a[0].s + 1);
      return (v[a[0].s] = 1), [v, 1];
    }
    a.sort(function (r, n) {
      return r.f - n.f;
    }),
      a.push({ s: -1, f: 25001 });
    var u = a[0],
      l = a[1],
      c = 0,
      h = 1,
      s = 2;
    for (a[0] = { s: -1, f: u.f + l.f, l: u, r: l }; h != o - 1; )
      (u = a[a[c].f < a[s].f ? c++ : s++]),
        (l = a[c != h && a[c].f < a[s].f ? c++ : s++]),
        (a[h++] = { s: -1, f: u.f + l.f, l: u, r: l });
    var w = i[0].s;
    for (f = 1; f < o; ++f) i[f].s > w && (w = i[f].s);
    var d = new n(w + 1),
      g = U(a[h - 1], d, 0);
    if (g > t) {
      f = 0;
      var p = 0,
        m = g - t,
        b = 1 << m;
      for (
        i.sort(function (r, n) {
          return d[n.s] - d[r.s] || r.f - n.f;
        });
        f < o;
        ++f
      ) {
        var y = i[f].s;
        if (!(d[y] > t)) break;
        (p += b - (1 << (g - d[y]))), (d[y] = t);
      }
      for (p >>>= m; p > 0; ) {
        var x = i[f].s;
        d[x] < t ? (p -= 1 << (t - d[x]++ - 1)) : ++f;
      }
      for (; f >= 0 && p; --f) {
        var M = i[f].s;
        d[M] == t && (--d[M], ++p);
      }
      g = t;
    }
    return [new r(d), g];
  },
  U = function (r, n, e) {
    return -1 == r.s
      ? Math.max(U(r.l, n, e + 1), U(r.r, n, e + 1))
      : (n[r.s] = e);
  },
  J = function (r) {
    for (var e = r.length; e && !r[--e]; );
    for (
      var t = new n(++e),
        a = 0,
        f = r[0],
        o = 1,
        i = function (r) {
          t[a++] = r;
        },
        v = 1;
      v <= e;
      ++v
    )
      if (r[v] == f && v != e) ++o;
      else {
        if (!f && o > 2) {
          for (; o > 138; o -= 138) i(32754);
          o > 2 &&
            (i(o > 10 ? ((o - 11) << 5) | 28690 : ((o - 3) << 5) | 12305),
            (o = 0));
        } else if (o > 3) {
          for (i(f), --o; o > 6; o -= 6) i(8304);
          o > 2 && (i(((o - 3) << 5) | 8208), (o = 0));
        }
        for (; o--; ) i(f);
        (o = 1), (f = r[v]);
      }
    return [t.subarray(0, a), e];
  },
  N = function (r, n) {
    for (var e = 0, t = 0; t < n.length; ++t) e += r[t] * n[t];
    return e;
  },
  z = function (r, n, e) {
    var t = e.length,
      a = O(n + 2);
    (r[a] = 255 & t),
      (r[a + 1] = t >>> 8),
      (r[a + 2] = 255 ^ r[a]),
      (r[a + 3] = 255 ^ r[a + 1]);
    for (var f = 0; f < t; ++f) r[a + f + 4] = e[f];
    return 8 * (a + 4 + t);
  },
  D = function (r, e, o, i, v, u, l, c, h, s, w) {
    A(e, w++, o), ++v[256];
    for (
      var d = F(v, 15),
        y = d[0],
        M = d[1],
        k = F(u, 15),
        C = k[0],
        E = k[1],
        O = J(y),
        S = O[0],
        U = O[1],
        D = J(C),
        $ = D[0],
        j = D[1],
        q = new n(19),
        B = 0;
      B < S.length;
      ++B
    )
      q[31 & S[B]]++;
    for (B = 0; B < $.length; ++B) q[31 & $[B]]++;
    for (
      var G = F(q, 7), H = G[0], I = G[1], K = 19;
      K > 4 && !H[f[K - 1]];
      --K
    );
    var L,
      P,
      Q,
      R,
      V = (s + 5) << 3,
      W = N(v, p) + N(u, m) + l,
      X =
        N(v, y) +
        N(u, C) +
        l +
        14 +
        3 * K +
        N(q, H) +
        (2 * q[16] + 3 * q[17] + 7 * q[18]);
    if (V <= W && V <= X) return z(e, w, r.subarray(h, h + s));
    if ((A(e, w, 1 + (X < W)), (w += 2), X < W)) {
      (L = g(y, M, 0)), (P = y), (Q = g(C, E, 0)), (R = C);
      var Y = g(H, I, 0);
      A(e, w, U - 257), A(e, w + 5, j - 1), A(e, w + 10, K - 4), (w += 14);
      for (B = 0; B < K; ++B) A(e, w + 3 * B, H[f[B]]);
      w += 3 * K;
      for (var Z = [S, $], _ = 0; _ < 2; ++_) {
        var rr = Z[_];
        for (B = 0; B < rr.length; ++B) {
          var nr = 31 & rr[B];
          A(e, w, Y[nr]),
            (w += H[nr]),
            nr > 15 && (A(e, w, (rr[B] >>> 5) & 127), (w += rr[B] >>> 12));
        }
      }
    } else (L = b), (P = p), (Q = x), (R = m);
    for (B = 0; B < c; ++B)
      if (i[B] > 255) {
        nr = (i[B] >>> 18) & 31;
        T(e, w, L[nr + 257]),
          (w += P[nr + 257]),
          nr > 7 && (A(e, w, (i[B] >>> 23) & 31), (w += t[nr]));
        var er = 31 & i[B];
        T(e, w, Q[er]),
          (w += R[er]),
          er > 3 && (T(e, w, (i[B] >>> 5) & 8191), (w += a[er]));
      } else T(e, w, L[i[B]]), (w += P[i[B]]);
    return T(e, w, L[256]), w + P[256];
  },
  $ = new e([
    65540, 131080, 131088, 131104, 262176, 1048704, 1048832, 2114560, 2117632,
  ]),
  j = function (f, o, i, v, l) {
    return (function (f, o, i, v, l, c) {
      var s = f.length,
        w = new r(v + s + 5 * (1 + Math.floor(s / 7e3)) + l),
        d = w.subarray(v, w.length - l),
        g = 0;
      if (!o || s < 8)
        for (var p = 0; p <= s; p += 65535) {
          var m = p + 65535;
          m < s
            ? (g = z(d, g, f.subarray(p, m)))
            : ((d[p] = c), (g = z(d, g, f.subarray(p, s))));
        }
      else {
        for (
          var b = $[o - 1],
            y = b >>> 13,
            x = 8191 & b,
            M = (1 << i) - 1,
            k = new n(32768),
            C = new n(M + 1),
            E = Math.ceil(i / 3),
            A = 2 * E,
            T = function (r) {
              return (f[r] ^ (f[r + 1] << E) ^ (f[r + 2] << A)) & M;
            },
            F = new e(25e3),
            U = new n(288),
            J = new n(32),
            N = 0,
            j = 0,
            q = ((p = 0), 0),
            B = 0,
            G = 0;
          p < s;
          ++p
        ) {
          var H = T(p),
            I = 32767 & p,
            K = C[H];
          if (((k[I] = K), (C[H] = I), B <= p)) {
            var L = s - p;
            if ((N > 7e3 || q > 24576) && L > 423) {
              (g = D(f, d, 0, F, U, J, j, q, G, p - G, g)),
                (q = N = j = 0),
                (G = p);
              for (var P = 0; P < 286; ++P) U[P] = 0;
              for (P = 0; P < 30; ++P) J[P] = 0;
            }
            var Q = 2,
              R = 0,
              V = x,
              W = (I - K) & 32767;
            if (L > 2 && H == T(p - W))
              for (
                var X = Math.min(y, L) - 1,
                  Y = Math.min(32767, p),
                  Z = Math.min(258, L);
                W <= Y && --V && I != K;

              ) {
                if (f[p + Q] == f[p + Q - W]) {
                  for (var _ = 0; _ < Z && f[p + _] == f[p + _ - W]; ++_);
                  if (_ > Q) {
                    if (((Q = _), (R = W), _ > X)) break;
                    var rr = Math.min(W, _ - 2),
                      nr = 0;
                    for (P = 0; P < rr; ++P) {
                      var er = (p - W + P + 32768) & 32767,
                        tr = (er - k[er] + 32768) & 32767;
                      tr > nr && ((nr = tr), (K = er));
                    }
                  }
                }
                W += ((I = K) - (K = k[I]) + 32768) & 32767;
              }
            if (R) {
              F[q++] = 268435456 | (u[Q] << 18) | h[R];
              var ar = 31 & u[Q],
                fr = 31 & h[R];
              (j += t[ar] + a[fr]), ++U[257 + ar], ++J[fr], (B = p + Q), ++N;
            } else (F[q++] = f[p]), ++U[f[p]];
          }
        }
        g = D(f, d, c, F, U, J, j, q, G, p - G, g);
      }
      return S(w, 0, v + O(g) + l);
    })(
      f,
      null == o.level ? 6 : o.level,
      null == o.mem
        ? Math.ceil(1.5 * Math.max(8, Math.min(13, Math.log(f.length))))
        : 12 + o.mem,
      i,
      v,
      !l
    );
  };
function q(r, n) {
  void 0 === n && (n = {});
  var e = (function () {
    var r = 1,
      n = 0;
    return {
      p: function (e) {
        for (var t = r, a = n, f = e.length, o = 0; o != f; ) {
          for (var i = Math.min(o + 5552, f); o < i; ++o) a += t += e[o];
          (t %= 65521), (a %= 65521);
        }
        (r = t), (n = a);
      },
      d: function () {
        return (
          (((r >>> 8) << 16) | ((255 & n) << 8) | (n >>> 8)) +
          2 * ((255 & r) << 23)
        );
      },
    };
  })();
  e.p(r);
  var t,
    a,
    f,
    o = j(r, n, 2, 4);
  return (
    (t = o),
    (a = n.level),
    (f = 0 == a ? 0 : a < 6 ? 1 : 9 == a ? 3 : 2),
    (t[0] = 120),
    (t[1] = (f << 6) | (f ? 32 - 2 * f : 1)),
    (function (r, n, e) {
      for (; e; ++n) (r[n] = e), (e >>>= 8);
    })(o, o.length - 4, e.d()),
    o
  );
}
function B(n, e) {
  return (function (n, e, o) {
    var i = n.length,
      u = !e || o,
      l = !o || o.i;
    o || (o = {}), e || (e = new r(3 * i));
    var h = function (n) {
        var t = e.length;
        if (n > t) {
          var a = new r(Math.max(2 * t, n));
          a.set(e), (e = a);
        }
      },
      s = o.f || 0,
      w = o.p || 0,
      d = o.b || 0,
      p = o.l,
      m = o.d,
      b = o.m,
      x = o.n,
      A = 8 * i;
    do {
      if (!p) {
        o.f = s = C(n, w, 1);
        var T = C(n, w + 1, 3);
        if (((w += 3), !T)) {
          var F = n[(H = O(w) + 4) - 4] | (n[H - 3] << 8),
            U = H + F;
          if (U > i) {
            if (l) throw "unexpected EOF";
            break;
          }
          u && h(d + F),
            e.set(n.subarray(H, U), d),
            (o.b = d += F),
            (o.p = w = 8 * U);
          continue;
        }
        if (1 == T) (p = y), (m = M), (b = 9), (x = 5);
        else {
          if (2 != T) throw "invalid block type";
          var J = C(n, w, 31) + 257,
            N = C(n, w + 10, 15) + 4,
            z = J + C(n, w + 5, 31) + 1;
          w += 14;
          for (var D = new r(z), $ = new r(19), j = 0; j < N; ++j)
            $[f[j]] = C(n, w + 3 * j, 7);
          w += 3 * N;
          var q = k($),
            B = (1 << q) - 1;
          if (!l && w + z * (q + 7) > A) break;
          var G = g($, q, 1);
          for (j = 0; j < z; ) {
            var H,
              I = G[C(n, w, B)];
            if (((w += 15 & I), (H = I >>> 4) < 16)) D[j++] = H;
            else {
              var K = 0,
                L = 0;
              for (
                16 == H
                  ? ((L = 3 + C(n, w, 3)), (w += 2), (K = D[j - 1]))
                  : 17 == H
                  ? ((L = 3 + C(n, w, 7)), (w += 3))
                  : 18 == H && ((L = 11 + C(n, w, 127)), (w += 7));
                L--;

              )
                D[j++] = K;
            }
          }
          var P = D.subarray(0, J),
            Q = D.subarray(J);
          (b = k(P)), (x = k(Q)), (p = g(P, b, 1)), (m = g(Q, x, 1));
        }
        if (w > A) throw "unexpected EOF";
      }
      u && h(d + 131072);
      for (
        var R = (1 << b) - 1, V = (1 << x) - 1, W = b + x + 18;
        l || w + W < A;

      ) {
        var X = (K = p[E(n, w) & R]) >>> 4;
        if ((w += 15 & K) > A) throw "unexpected EOF";
        if (!K) throw "invalid length/literal";
        if (X < 256) e[d++] = X;
        else {
          if (256 == X) {
            p = null;
            break;
          }
          var Y = X - 254;
          if (X > 264) {
            var Z = t[(j = X - 257)];
            (Y = C(n, w, (1 << Z) - 1) + v[j]), (w += Z);
          }
          var _ = m[E(n, w) & V],
            rr = _ >>> 4;
          if (!_) throw "invalid distance";
          if (
            ((w += 15 & _),
            (Q = c[rr]),
            rr > 3 && ((Z = a[rr]), (Q += E(n, w) & ((1 << Z) - 1)), (w += Z)),
            w > A)
          )
            throw "unexpected EOF";
          u && h(d + 131072);
          for (var nr = d + Y; d < nr; d += 4)
            (e[d] = e[d - Q]),
              (e[d + 1] = e[d + 1 - Q]),
              (e[d + 2] = e[d + 2 - Q]),
              (e[d + 3] = e[d + 3 - Q]);
          d = nr;
        }
      }
      (o.l = p),
        (o.p = w),
        (o.b = d),
        p && ((s = 1), (o.m = b), (o.d = m), (o.n = x));
    } while (!s);
    return d == e.length ? e : S(e, 0, d);
  })(
    ((function (r) {
      if (8 != (15 & r[0]) || r[0] >>> 4 > 7 || ((r[0] << 8) | r[1]) % 31)
        throw "invalid zlib data";
      if (32 & r[1])
        throw "invalid zlib data: preset dictionaries not supported";
    })(n),
    n.subarray(2, -4)),
    e
  );
}
function G(n, e) {
  var t = n.length;
  if (!e && "undefined" != typeof TextEncoder)
    return new TextEncoder().encode(n);
  for (
    var a = new r(n.length + (n.length >>> 1)),
      f = 0,
      o = function (r) {
        a[f++] = r;
      },
      i = 0;
    i < t;
    ++i
  ) {
    if (f + 5 > a.length) {
      var v = new r(f + 8 + ((t - i) << 1));
      v.set(a), (a = v);
    }
    var u = n.charCodeAt(i);
    u < 128 || e
      ? o(u)
      : u < 2048
      ? (o(192 | (u >>> 6)), o(128 | (63 & u)))
      : u > 55295 && u < 57344
      ? (o(
          240 |
            ((u = (65536 + (1047552 & u)) | (1023 & n.charCodeAt(++i))) >>> 18)
        ),
        o(128 | ((u >>> 12) & 63)),
        o(128 | ((u >>> 6) & 63)),
        o(128 | (63 & u)))
      : (o(224 | (u >>> 12)), o(128 | ((u >>> 6) & 63)), o(128 | (63 & u)));
  }
  return S(a, 0, f);
}
function H(r, n) {
  var e = "";
  if (!n && "undefined" != typeof TextDecoder)
    return new TextDecoder().decode(r);
  for (var t = 0; t < r.length; ) {
    var a = r[t++];
    a < 128 || n
      ? (e += String.fromCharCode(a))
      : a < 224
      ? (e += String.fromCharCode(((31 & a) << 6) | (63 & r[t++])))
      : a < 240
      ? (e += String.fromCharCode(
          ((15 & a) << 12) | ((63 & r[t++]) << 6) | (63 & r[t++])
        ))
      : ((a =
          (((15 & a) << 18) |
            ((63 & r[t++]) << 12) |
            ((63 & r[t++]) << 6) |
            (63 & r[t++])) -
          65536),
        (e += String.fromCharCode(55296 | (a >> 10), 56320 | (1023 & a))));
  }
  return e;
}
const I = "v1",
  K = (r) => {
    const n = { ...r, v: I };
    return H(q(G(JSON.stringify(n))), !0);
  },
  L = (r) => {
    if ("string" != typeof r) return r;
    try {
      const n = JSON.parse(r);
      if (n.timestamp) return n;
    } catch (r) {}
    try {
      const n = JSON.parse(H(B(G(r, !0))));
      if (n.v === I) return n;
      throw new Error(
        `These events were packed with packer ${n.v} which is incompatible with current packer ${I}.`
      );
    } catch (r) {
      throw (console.error(r), new Error("Unknown data format."));
    }
  };
window.pack = K;
//# sourceMappingURL=/sm/79d152138fed2e0ab088dabbfe1d2c874957b982d1c135d33b80804daf88fa8f.map
