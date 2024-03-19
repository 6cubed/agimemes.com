AGI-generated meme timeline.

https://agimemes.com

<img width="248" alt="Screenshot 2024-03-18 at 22 00 31" src="https://github.com/6cubed/agimemes.com/assets/162924902/442b2d5e-9947-4a87-a28a-780bcc2dedbf">

# Prompting

## Personality-based prompting.
The idea would be to tell the LLM to take on a given personality before thinking of a meme. 
Somewhat winded down this approach as it didn't seem to be a very promising avenue in initial tests.

## Chain-of-thought prompting.
Since chain-of-thought prompting has shown uplfift on many general LLM tasks, it stands to reason that it is also going to make the memes funnier. A first experiment could be to ask the LLM to explain why its caption is funny and then give it an opportunity to revise its output to be even funnier.

## Few-shot prompting.
Early indications that this technique is particularly useful for controlling the format of the output of the LLM, so we currently use it for the chatgpt memes. 

More experimenting needed to see if it can also be useful for making the LLM funnier. There would be some overhead associated with maintaining meme-specific few-shot examples but a few general examples might already prove useful.

# Fresh information sources.

## News API
We currently search for techcrunch articles and any articles mentioning the term "Artificial Intelligence".

## Twitter
Twitter and any other realtime comment sections could be very powerful source for us to create highly relevant memes with viral potential.

# Models
## Mistral
Implemented. Health metrics to follow.
## Mistral Neets.ai fork
Implemented. Health metrics to follow.
## ChatGPT
Implemented. Health metrics to follow.
## Fine-tuned ChatGPT
Coming soon.
## Grok
Coming soon (maybe). 

# Memes
## Imgflip static list
https://api.imgflip.com/get_memes

We are outsourcing everything to do with the meme images to Imgflip for now. It's made everything much quicker to set up.

## Automatic template tweaking (meme adaptation)
This is a longer term ambitious goal. Likely a big rabbit hole (multimodal models etc.) and likely tough to get it working correctly. Prefer to focus on making the finite list of meme templates funny first. 

# Benchmarks / tracked metrics
Some healthy competition between the models could help to advance the quality of the memes. To that effect a leaderboard of some health metrics would be a nice addition at some stage.

## Social shares per meme created
## Prompt health (creations per attempted)
## % manually reviewed "Good memes"

No unit tests please.
