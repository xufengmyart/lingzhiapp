#!/bin/bash
# 生态之梦风格部署
curl -fsSL https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/public.tar_0a9303df.gz?sign=1770365987-89a7ccaed1-0-8e778b4dede38c056e5948ee0278b68e035c34b674cb76d2aea22ef96b8b1679 -O /tmp/public.tar.gz && \
cd /var/www/frontend && \
rm -rf * && \
tar -xzf /tmp/public.tar.gz && \
chown -R root:root . && \
chmod -R 755 . && \
systemctl reload nginx && \
echo "✅ 生态之梦风格部署完成！清除缓存后访问 https://meiyueart.com/dream-selector"
