# RAG AI Assistant
In [Creating Your First Assistant](./creating-your-first-assistant.md), we took a look at how to create an assistant that uses Retrieval-Augmented Generation (RAG) to answer questions from a document of our choosing. Here, we'll expand on that process by using the Opsloom documentation (that's what you're reading now!) as a knowledge base. The end goal will be to create an assistant that can give answers about setting up and using Opsloom to make for even quicker onboarding.

## Creating the Knowledge Base

Make sure that your API and database are up and running on your local machine. Then pull up [Bruno](https://www.usebruno.com/) and ensure your environment is configured properly. For instructions on this, check out the *Creating the Knowledge Base* section in [Creating Your First Assistant](./creating-your-first-assistant.md).

Modify the `kbase/create` body to the following:

```JSON
{
  "name": "opsloom_kbase",
  "description": "Opsloom Knowledge Base"
}
```

Then call the endpoint. As before, verify that everything worked by invoking `kbase/list`. You should see your new knowledge base there alongside any defaults or previously created knowledge bases.

## Adding Multiple Documents

Instead of supplying the knowledge base with a single document, we're going to use many documents—one for each page of this documentation. Download the following PDFs:

- [Introduction](./assets/introduction.pdf)
- [Architecture](./assets/architecture.pdf)
- [Setting Up Locally](./assets/setting-up-locally.pdf)
- [Creating Your First Assistant](./assets/creating-your-first-assistant.pdf)
- [Styling](./assets/styling.pdf)
- [Embedding](./assets/embedding.pdf)
- [FAQs](./assets/faqs.pdf)

In Bruno, open up the `index/index_document` endpoint and attach the first PDF in the body tab. Make sure the `kbase_name` parameter is set to `opsloom_kbase`. Call the API, ensuring you get an S3 URI back as confirmation that the call was successful. Repeat this process with the following PDFs until they are all in the knowledge base.

## Creating the Assistant
We'll need to customize the body of the `assistant/create_assistant` endpoint in order to account for our particular use case. Make the following changes:

- Set `name` to *"openai_ops."*
- Set `config/type` to *"rag."*
- Set `metadata/title` to *"About Opsloom."*
- Set `metadata/description` to *"An AI Guide to Opsloom: What It Can Do and How To Set It Up."*
- Set `system_prompts/system` to the following:

> You are a manager at a company tasked with responding to all questions related to the software Opsloom. You are to respond only using the data in the Opsloom documentation. Expect questions related to the purpose of Opsloom, as well as how to install and embed Opsloom. Be concise and grammatically correct.

- Set `system_prompts/prompts` to:
  - *"What is Opsloom?"*
  - *"What software do I need installed on my computer to run Opsloom?"*
  - *"How do I embed Opsloom on my website?"*

With all of the changes in place, call the endpoint to create your new assistant.

## Testing the Assistant
The Opsloom assistant should now be visible when you run the frontend locally. Ask it some questions to verify that it's using the knowledge base properly. If you would like to customize it further, either recreate the assistant with the same knowledge base and a different prompt, or check out some of our articles on [customization](./styling.md).
