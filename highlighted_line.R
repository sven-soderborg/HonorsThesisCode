# Create a highlighted line chart
library(ggplot2)
library(gghighlight)
library(dplyr)

work_dir <- setwd("C:/Users/svens/Documents/HonorsThesisCode")

# Read in the Electricity Generation Data
state_pct <- read.csv("Data/EIA/state_ren_pct.csv", header = TRUE, sep = ",") %>%
  mutate(state = toupper(state)) 

p = ggplot(state_pct, aes(x = year, y = pct_renew, color = state)) +
  geom_line(size = 1.2) +  # Thicker lines
  scale_y_continuous(labels = scales::percent_format(scale = 1),
                     name = "% from Renewables") +
  scale_x_continuous(breaks = seq(min(state_pct$year), max(state_pct$year), by = 5), name="Year") +  # x-axis breaks every 5 years
  gghighlight(state %in% c("UT", "IA", "ID", "TX", "CA")) +  # Highlight selected states
  ggtitle("% of Electricity from Renewables in Each State") +
  theme_minimal()
p
ggsave("Visuals/pct_ren_highlighted.png", plot = p+
         theme(plot.background = element_rect(color = "WHITE"),
               plot.title = element_text(size=25, hjust=.5)), width = 10, height = 8,
       dpi = 700, units = "in", device='png')
