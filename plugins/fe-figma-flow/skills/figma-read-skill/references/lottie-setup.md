# Lottie 动效接入参考

## lottie.js 工具文件模板

当项目中**尚未使用过 lottie** 或 **没有封装drawLottie方法** 时，在项目中创建公用工具文件，并安装 `@guanghe-pub/onion-utils`：

```typescript
import { dynamicCDN } from '@guanghe-pub/onion-utils'

declare global {
  interface Window {
    lottie: any
  }
}

const CDN = [
  {
    name: 'lottie',
    url: '//fp.yangcong345.com/middle/5.7.0/lottie_svg.min.js',
  },
]
const options = {
  type: 'text/javascript',
  crossOrigin: 'anonymous',
}

export async function loadLottie() {
  await dynamicCDN.load(CDN, options)
  return window.lottie
}

export async function drawLottie(options) {
  const lottie = await loadLottie()
  return lottie.loadAnimation(options)
}

export default loadLottie
```

## 使用示例

```typescript
import { drawLottie } from '@util/lottie'

const lottieRef = ref<HTMLElement | null>(null)
const LOTTIE_URL = 'https://fp.yangcong345.com/xxx/data.json'

onMounted(() => {
  if (lottieRef.value && LOTTIE_URL) {
    drawLottie({
      container: lottieRef.value,
      path: LOTTIE_URL,
      renderer: 'svg',
      loop: true,
      autoplay: true,
    })
  }
})
```

```html
<div ref="lottieRef" class="lottie-container"></div>
```

## 链接格式处理

| 链接格式 | 处理方式 |
| --- | --- |
| `lottie-https://fp.yangcong345.com/.../data.json` | 直接使用链接加载 |
| `lottie-https://lottiefiles.com/animations/xxx` | 获取对应 JSON 文件链接，或添加 TODO 注释 |
| `lottie-xxx`（无有效链接） | 创建容器元素，添加 TODO 注释标明需要链接 |
