---
layout: default
title: Tech Archive
permalink: /tech/
---

{%- assign tech_posts = site.posts | where_exp: "item", "item.categories contains 'tech' or item.categories contains 'it'" -%}
{%- assign life_posts = site.posts | where_exp: "item", "item.categories contains 'life'" -%}

<div class="category-page">
  <div class="hero-section">
    <h1 class="hero-title">💻 기술 문서 (Tech)</h1>
    <p class="hero-subtitle">
      서버 구축, 인프라 운영, 환경 설정 및 개발 학습 과정에서 얻은 경험을 기록한 기술 아카이브입니다.
    </p>

    <div class="category-chips">
      <a href="{{ "/" | relative_url }}" class="category-chip">
        <span>전체 글</span>
        <span class="count">{{ site.posts.size }}</span>
      </a>
      <a href="{{ "/tech/" | relative_url }}" class="category-chip active">
        <span>💻 기술 문서 (Tech)</span>
        <span class="count">{{ tech_posts.size }}</span>
      </a>
      <a href="{{ "/life/" | relative_url }}" class="category-chip">
        <span>🌿 일상 생활 (Life)</span>
        <span class="count">{{ life_posts.size }}</span>
      </a>
    </div>
  </div>

  <div class="section-header">
    <h2 class="section-title">기술 문서 목록 (총 {{ tech_posts.size }}편)</h2>
  </div>

  <div class="post-list">
    {%- if tech_posts.size > 0 -%}
      {%- for post in tech_posts -%}
        <article class="post-card">
          <a href="{{ post.url | relative_url }}">
            <div class="post-card-header">
              <span class="badge badge-tech">Tech</span>
              <time class="post-date" datetime="{{ post.date | date_to_xmlschema }}">
                {{ post.date | date: "%Y.%m.%d" }}
              </time>
            </div>

            <h3 class="post-card-title">{{ post.title | escape }}</h3>

            {%- if post.excerpt -%}
              <p class="post-card-excerpt">
                {{ post.excerpt | strip_html | strip_newlines | truncate: 160 }}
              </p>
            {%- endif -%}
          </a>

          {%- if post.tags and post.tags.size > 0 -%}
            <div class="post-card-footer">
              <div class="post-tags">
                {%- for tag in post.tags -%}
                  <span class="post-tag">#{{ tag }}</span>
                {%- endfor -%}
              </div>
            </div>
          {%- endif -%}
        </article>
      {%- endfor -%}
    {%- else -%}
      <p style="color: var(--text-muted); padding: 2rem 0;">등록된 기술 문서가 없습니다.</p>
    {%- endif -%}
  </div>
</div>
