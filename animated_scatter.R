library(ggplot2)
library(gganimate)

setwd("C:/Users/svens/Documents/HonorsThesisCode")


# Read in the Electricity Generation Data
state_pct <- read.csv("Data/EIA/state_ren_pct.csv", header = TRUE, sep = ",") %>%
  mutate(state = toupper(state)) 

options(gganimate.dev_args = list(width = 7, height = 5, units = 'in', res=320))

p <- ggplot(state_pct, aes(genMWH_renew, pct_renew, color = state, size=genMWH)) +
  geom_point(alpha=0.7) +
  geom_label(data=state_pct %>% filter(pct_renew>22 | genMWH_renew>20000000),
             aes(label=state), size=2, nudge_x = 0.5, nudge_y = 0.5) +
  transition_time(year) +
  labs(title = "Energy Portfolio Percentages by State",
       subtitle = "Year: {frame_time}",
       caption = "Data Source: EIA",
       y = "% of Generation from Renewables",
       x = "Megawatthours Generated from Renewables") +
  scale_fill_viridis_d() +
  theme_minimal() +
  ease_aes('linear') +
  guides(color=FALSE, size=guide_legend("Total Generation (MWH)"))
animate(p, fps=10, duration=10)
anim_save("Visuals/state_pct1.gif")
