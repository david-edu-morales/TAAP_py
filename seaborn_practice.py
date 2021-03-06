# %% 
import seaborn as sns

# %%
penguins = sns.load_dataset("penguins")
# %%
sns.histplot(data=penguins, x='flipper_length_mm', hue='species', multiple='stack')
# %%
sns.displot(data=penguins, x="flipper_length_mm", hue="species", multiple="stack")
# %%
sns.displot(data=penguins, x="flipper_length_mm", hue="species", col="species")
# %%
