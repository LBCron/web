# DNS: agenticstack.cl y theagenticstack.cl

Ambos dominios están registrados en **NIC Chile**. NIC Chile delega la resolución a los **servidores DNS** que indiques en _Mis dominios → Configuración técnica → Servidores DNS_; los registros (A, AAAA, CNAME, TXT) se crean en ese proveedor DNS, no en NIC Chile.

**Recomendación:** usar Cloudflare (plan gratuito) como DNS de ambos dominios. Cualquier otro DNS sirve igual para `agenticstack.cl`; Cloudflare además resuelve gratis la redirección de `theagenticstack.cl` con HTTPS.

## 0. Verificar el dominio en la organización (antes de todo)

Evita que otra cuenta de GitHub tome el dominio ([docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)).

1. GitHub → organización `agentic-stack-cl` → _Settings → Pages → Add a domain_ → `agenticstack.cl`.
2. GitHub muestra un registro TXT como `_github-pages-challenge-agentic-stack-cl.agenticstack.cl` con un valor aleatorio. Créalo en el DNS (paso 2) y presiona _Verify_.

## 1. Delegar en NIC Chile

Para **cada** dominio: crea la zona en Cloudflare (_Add a domain_ → plan Free), copia los dos nameservers que te asigna (p. ej. `xxx.ns.cloudflare.com`) y reemplaza los servidores DNS en NIC Chile. La propagación puede tardar hasta 24 h.

## 2. Registros de `agenticstack.cl` (principal)

Valores oficiales de GitHub Pages ([docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)). En Cloudflare, todos en **DNS only** (nube gris): si se proxifican, GitHub no puede emitir el certificado HTTPS.

| Tipo  | Nombre                                     | Valor                                   |
| ----- | ------------------------------------------ | --------------------------------------- |
| A     | `@`                                        | `185.199.108.153`                       |
| A     | `@`                                        | `185.199.109.153`                       |
| A     | `@`                                        | `185.199.110.153`                       |
| A     | `@`                                        | `185.199.111.153`                       |
| AAAA  | `@`                                        | `2606:50c0:8000::153`                   |
| AAAA  | `@`                                        | `2606:50c0:8001::153`                   |
| AAAA  | `@`                                        | `2606:50c0:8002::153`                   |
| AAAA  | `@`                                        | `2606:50c0:8003::153`                   |
| CNAME | `www`                                      | `agentic-stack-cl.github.io`            |
| TXT   | `_github-pages-challenge-agentic-stack-cl` | (valor que entrega GitHub en el paso 0) |

No uses registros comodín (`*`).

## 3. Activar el dominio en el repo

Cuando `dig agenticstack.cl +short` devuelva las IPs de arriba:

```bash
gh api -X PUT repos/agentic-stack-cl/web/pages -f cname=agenticstack.cl
# cuando GitHub termine de emitir el certificado (minutos a horas):
gh api -X PUT repos/agentic-stack-cl/web/pages -F https_enforced=true
```

(O en _Settings → Pages → Custom domain_.) El archivo `public/CNAME` ya contiene `agenticstack.cl`; con despliegue por Actions GitHub usa el valor configurado en Settings, el archivo queda como documentación.

`www.agenticstack.cl` redirige solo a `agenticstack.cl` gracias al CNAME `www`.

## 4. Redirección de `theagenticstack.cl`

**Opción A — Cloudflare (recomendada, con HTTPS):**

1. En la zona `theagenticstack.cl`, crea registros **proxificados** (nube naranja): `A @ 192.0.2.1` y `A www 192.0.2.1` (IP de documentación; Cloudflare responde antes de llegar ahí).
2. _Rules → Redirect Rules → Create rule_ → "All incoming requests" → _Dynamic_ → expresión `concat("https://agenticstack.cl", http.request.uri.path)`, código **301**, conservar query string.

**Opción B — Redirección web de NIC Chile:** NIC Chile ofrece una redirección web gratuita en la configuración técnica del dominio. Es lo más simple, pero reemplaza los servidores DNS del dominio y conviene comprobar que redirija también las peticiones `https://`.

## 5. Comprobar

```bash
dig agenticstack.cl +short          # 4 IPs 185.199.10x.153
dig AAAA agenticstack.cl +short     # 4 IPs 2606:50c0:800x::153
dig www.agenticstack.cl +short      # agentic-stack-cl.github.io. + IPs
curl -sI https://theagenticstack.cl | grep -i location   # https://agenticstack.cl/
curl -sI https://agenticstack.cl | head -1                 # HTTP/2 200
```
