# file: credit_risk_sim.py
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

# --- 1. Define Portfolio & Risk Parameters ---
# These would be the inputs to your model
num_simulations = 10000
num_loans = 2000
loan_value = 100000
prob_of_default = 0.05  # Average probability of default for each loan
loss_given_default = 0.60 # The fraction of the loan lost if a default occurs

# --- 2. Run the Monte Carlo Simulation ---
# Simulate thousands of possible futures for our portfolio
defaults = np.random.binomial(n=1, p=prob_of_default, size=(num_simulations, num_loans))
portfolio_losses = np.sum(defaults * loan_value * loss_given_default, axis=1)

# --- 3. Calculate Key Risk Metrics ---
expected_loss = np.mean(portfolio_losses)
value_at_risk_95 = np.percentile(portfolio_losses, 95) # 95% Value at Risk (VaR)
max_loss = np.max(portfolio_losses)

# --- 4. Generate Output (Text and Plot) ---
text_result = (
    f"Simulation Results:\n"
    f"  - Expected Portfolio Loss: ${expected_loss:,.2f}\n"
    f"  - 95% Value at Risk (VaR): ${value_at_risk_95:,.2f}\n"
    f"  - Maximum Simulated Loss: ${max_loss:,.2f}"
)
print(text_result)

# Create a histogram of potential losses
fig, ax = plt.subplots()
ax.hist(portfolio_losses, bins=50, density=True)
ax.set_title('Distribution of Potential Portfolio Losses')
ax.set_xlabel('Loss Amount ($)')
ax.set_ylabel('Probability Density')

# Convert plot to Base64 to be saved by the C++ worker
buf = io.BytesIO()
fig.savefig(buf, format='png')
buf.seek(0)
image_base64 = base64.b64encode(buf.read()).decode('utf-8')

print("\n---PLOT_START---")
print(image_base64)
print("---PLOT_END---")