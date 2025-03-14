---
layout: home
---
<script setup>
  import { shallowRef } from 'vue';
  import GithubSVG from './lib/assets/github.svg?component';
  import PlaySVG from './lib/assets/play.svg?component';

  import LayersSVG from './lib/assets/svg/layers.svg?component';
  import BlocksSVG from './lib/assets/svg/blocks.svg?component';
  import CodeSVG from './lib/assets/svg/code.svg?component';
  import BrushSVG from './lib/assets/svg/brush.svg?component';
  import PhoneSVG from './lib/assets/svg/phone.svg?component';
  import AgentSVG from './lib/assets/svg/agent.svg?component';

  const cards = shallowRef( [
    {
        icon: LayersSVG,
        title: "Interactive Chatbot Interface",
        body: "Provides seamless interaction capabilities with built-in features to store and retrieve conversation history, ensuring contextual continuity."
    },
        {
        icon: BlocksSVG,
        title: "Custom Assistant Framework",
        body: "A robust foundation for building and integrating tailored assistants to meet specific enterprise needs."
    },
        {
        icon: CodeSVG,
        title: "Agentic Framework",
        body: "Provides an agentic interface to interact with LLMs with constructs such as agents and tools to accomplish complex tasks."
    },
        {
        icon: CodeSVG,
        title: "Embeddable Design",
        body: "Optimized for embedding chatbot experiences into existing applications and ecosystems, enabling smooth integration with enterprise workflows.  "
    },
    {
        icon: BrushSVG,
        title: "Customizable Look and Feel",
        body: "Offers easy-to-use options for branding and interface customization to align with organizational identity."
    },
    {
        icon: PhoneSVG,
        title: "Responsive Mobile-Friendly Design",
        body: " Ensures accessibility and usability across devices with a fully responsive interface."
    }
  ])

  const assistants = shallowRef( [
    {
        title: "Product Support Assistant",
        body: "A conversational assistant designed to navigate Opsloom documentation, offering quick and accurate product support for users",
        src: "landing/avatar/docs.jpg",
        alt: "random documents",
        href:"/rag-assistant",
    },
    {
        title: "Data Insights Assistant (Text-to-SQL)",
        body: "Enables users to query data interactively, transforming natural language queries into SQL. This example focuses on AWS cost analytics for insights",
        src: "landing/avatar/data.jpg",
        alt: "random data",
        href:"/text-to-sql-assistant",
    },
    {
        title: "Rules Engine Assistant",
        body: "Allows articulation of complex business rules and evaluates them dynamically. Integrated with cost analytics, it demonstrates rule-based decision-making tailored to specific needs",
        src: "landing/avatar/list.jpg",
        alt: "lists pinned to a wall",
        href:"",
    },
    {
        title: "Custom Workflow Assistant",
        body: "Configurable workflows designed for small businesses. Build assistants such as lead capture directly on your website",
        src: "landing/avatar/business.jpg",
        alt: "business",
        href:"",
    },
  ])

  const openLink = (href) => {
    window.open(href, '_blank')
  }
</script>

<div class="w-full pt-16">
  <div class="relative grid sm:grid-cols-[5fr_1fr] w-full">
    <div class="pt-16">
      <h1 class="!text-[60px] lg:!text-[75px] !leading-[1.1em] !font-bold pb-4">
        Blueprint for building <br/> Enterprise AI Apps
      </h1>
      <p class="!leading-[1.5em] max-w-[500px]">
        Build light weight custom chat expreiences, workflows and automations to help your business enter the AI era.
      </p>
      <div class="pt-6 flex flex-col sm:flex-row gap-4 [&>*]:w-full sm:[&>*]:w-fit">
        <a href="/introduction" class="px-10 py-1 bg-[#1f6feb] rounded-full flex items-center justify-center [&:not(:hover)]:!text-[white] !no-underline">
          <PlaySVG class="mr-2 w-[25px]"/>
          <p>
            See Docs
          </p>
        </a>
        <button class="px-10 py-4 rounded-full flex items-center justify-center" style="border: 1px solid #1f6feb">
          <GithubSVG class="w-[30px] mr-2"/> 
          View on Github
        </button>
      </div>
    </div>
    <div class="absolute right-0 top-0 bg-[#8f98d812] flex items-center justify-center rounded-3xl h-[500px] w-[700px] pointer-events-none">
      <img src="/landing/grid.png" alt="grid" class="absolute opacity-10 h-full top-0"/>
      <img src="/landing/star.svg" class="hidden lg:block animate-spin" style="animation-duration: 15s "/>
    </div>
  </div>
</div>

<div class="w-full pt-36"></div>

# Features
<div class="w-full pt-6">
  <div class="grid md:grid-cols-2 xl:grid-cols-3 gap-7">
    <div v-for="({title, body, icon}, idx) in cards" class="group relative flex flex-col bg-[#8f98d812] p-6 rounded-r-2xl md:rounded-2xl">
      <component :is="icon" class="w-[50px] mr-2 fill-[#9ca6dd1f] "/>
      <h3 class="!mt-6">{{ title }}</h3>
      <p>
        {{ body }}
      </p>
      <div class="absolute -left-[100px] top-0 w-[100px] h-full bg-[#8f98d812] md:hidden"/>
    </div>
  </div>
</div>

<div class="w-full pt-2 mt-20">
  <div class="w-full h-fit md:p-6 rounded-3xl bg-[#8f98d812] flex items-center justify-center">
    <!-- 
    Couple of videos, for each sample. Should probably load it on you tube or host somewhere else and provide the references
    -->
    <video width="1200" height="614" autoplay loop muted class="hidden sm:block rounded-3xl opacity-90">
      <source src="/landing/demo.mp4" type="video/mp4">
          Your browser does not support the video tag.
    </video>
    <video autoplay loop muted class="-mt-8 sm:hidden rounded-xl opacity-90">
      <source src="/landing/demo-sm.mp4" type="video/mp4">
          Your browser does not support the video tag.
    </video>
  </div>
  <div>
  </div>
  <div>
  </div>
</div>

<div class="w-full pt-20"></div>

# Sample Assistants

Explore a variety of use cases addressed by Opsloom, each showcasing its versatility and enterprise readiness. Click on the examples to access working demos:

<div class="w-full pt-10">
  <div class="grid md:grid-cols-2 xl:grid-cols-4 gap-7">
    <div v-for="({title, body, src, href, alt}, idx) in assistants" class="group relative flex flex-col border-[#b9a5a536] border-t border-r border-b md:border-l p-6 rounded-r-2xl md:rounded-2xl cursor-pointer hover:bg-opacity-10 hover:bg-[#1f6feb] transition-colors" @click="!!href && openLink(href)" >
      <img :src="src" :alt="alt" class="self-center rounded-full h-[75px] w-[75px] object-cover group-hover:scale-105 transition-transform"/>
      <h3 class="text-center !mt-6">{{ title }}</h3>
      <p class="text-center">
        {{ body }}
      </p>
      <div class="absolute -left-[100px] -top-[1px] w-[100px] h-[calc(100%+2px)] md:hidden border-[#b9a5a536] group-hover:bg-opacity-10 group-hover:bg-[#1f6feb] transition-colors border-y"/>
    </div>
  </div>
  <a href="/setting-up-locally" class="mt-12 mx-auto w-[250px] px-10 bg-[#1f6feb] rounded-full flex items-center justify-center [&:not(:hover)]:!text-[white] !no-underline">
    <PlaySVG class="mr-2 w-[25px]"/>
    <p>
      Try it yourself
    </p>
  </a>
  <p class="text-center !mt-6">
    Each assistant demonstrates the power and flexibility of Opsloom in addressing diverse enterprise challenges.
  </p>
</div>



