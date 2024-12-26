<script lang="ts" setup>
interface Post {
  id: string
  slug: string
  body: string
  data: Record<string, any>
  collection: string
  render: any
}

withDefaults(defineProps<{
  list: Post[]
}>(), {
  list: () => [],
})

function getDate(date: string) {
  return new Date(date).toISOString()
}

function getHref(post: Post) {
  if (post.data.redirect)
    return post.data.redirect
  return `/posts/${post.slug}`
}

function getTarget(post: Post) {
  if (post.data.redirect)
    return '_blank'
  return '_self'
}

function isSameYear(a: Date | string | number, b: Date | string | number) {
  return a && b && getYear(a) === getYear(b)
}

function getYear(date: Date | string | number) {
  return new Date(date).getFullYear()
}
</script>

<template>
  <ul sm:min-h-38 min-h-28 mb-18>
    <template v-if="!list || list.length === 0">
      <div my-12 opacity-50>
        nothing here yet.
      </div>
    </template>
    <li v-for="(post, index) in list " :key="post.data.title" mb-8>
      <div v-if="!isSameYear(post.data.date, list[index - 1]?.data.date)" select-none relative h18 pointer-events-none>
        <span text-7em color-transparent font-bold text-stroke-2 text-stroke-hex-aaa op-20 absolute top--0.2em>
          {{ getYear(post.data.date) }}
        </span>
      </div>
      <a text-lg lh-tight nav-link flex="~ col gap-2" :aria-label="post.data.title" :target="getTarget(post)" :href="getHref(post)">
        <div flex="~ col md:row gap-2 md:items-center">
          <div flex="~ gap-2 items-center text-wrap">
            <span lh-normal>
              <i v-if="post.data.draft" text-base vertical-mid i-ri-draft-line />
              {{ post.data.title }}
            </span>
          </div>
          <div opacity-70 text-sm ws-nowrap flex="~ gap-2 items-center">
            <i v-if="post.data.redirect" text-base i-ri-external-link-line />
            <i v-if="post.data.recording || post.data.video" text-base i-ri:film-line />
            <time v-if="post.data.date" :datetime="getDate(post.data.date)">{{ post.data.date.split(',')[0] }}</time>
            <span v-if="post.data.duration">· {{ post.data.duration }}</span>
            <span v-if="post.data.tags">
              <!-- tags should have rounded borders like clips -->
              <span v-for="tag in post.data.tags" :key="tag" class="tag">{{ tag }}</span>
            </span>
          </div>
        </div>
        <div opacity-70 text-sm>{{ post.data.description }}</div>
      </a>
    </li>
  </ul>
  <style>
    .tag {
    display: inline-block;
    background-color: lightgray; /* light background color */
    border: 1px solid #ccc; /* chip-style border */
    border-radius: 20%; /* rounded corners */
    padding: 0.2em 0.4em; /* padding for the chip look */
    margin-right: 8px; /* space between chips */
    font-size: 14px; /* font size adjustment */
    color: #333; /* text color */
    }
  </style>
</template>
