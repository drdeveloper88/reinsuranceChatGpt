"""
Sample insurance data for seeding the chatbot knowledge base
"""

INSURANCE_SAMPLES = {
    "health": [
        """
        HEALTH INSURANCE POLICY OVERVIEW
        
        Coverage Types:
        - Preventive Care: Annual physical exams, vaccinations, screening tests (100% covered)
        - Doctor Visits: $25 copay for in-network, $50 for out-of-network
        - Emergency Room: $500 copay per visit, waived if admitted
        - Hospital Stays: 80% covered after deductible
        - Prescription Drugs: Tier 1 ($10), Tier 2 ($25), Tier 3 ($50)
        
        Deductibles:
        - Individual: $1,500 per year
        - Family: $3,000 per year
        - Preventive care has no deductible
        
        Out-of-Pocket Maximum: $5,500 individual / $11,000 family
        """,
        
        """
        HEALTH INSURANCE EXCLUSIONS
        
        The following are NOT covered:
        - Cosmetic procedures
        - Weight loss programs
        - Fertility treatments (except for PCOS)
        - Mental health: Limited to 30 visits per year
        - Alternative medicine: Acupuncture, homeopathy
        - Over-the-counter medications
        - Non-emergency services outside the US
        
        Pre-authorization Required:
        - Any non-emergency surgery
        - Imaging (MRI, CT scans)
        - Specialist referrals
        - Extended hospital stays (>5 days)
        """,
    ],
    
    "property": [
        """
        HOMEOWNERS INSURANCE COVERAGE
        
        Dwelling Coverage (Building Structure):
        - Covers repairs/rebuilding up to policy limit
        - Includes roof, walls, floors, built-in appliances
        - Covered events: Fire, theft, vandalism, storm damage
        
        Personal Property Coverage:
        - Covers furniture, electronics, clothing (50-75% of dwelling coverage)
        - Replacement cost or actual cash value based on policy
        
        Liability Coverage:
        - Standard: $100,000
        - Optional: Up to $500,000
        - Covers medical expenses if someone is injured on your property
        - Includes legal defense costs
        
        Deductible: $500 (standard) or $1,000 (optional)
        Additional Living Expenses: Up to 20% of dwelling coverage
        """,
        
        """
        HOMEOWNERS INSURANCE EXCLUSIONS
        
        NOT Covered:
        - Floods (separate flood insurance required)
        - Earthquakes (separate earthquake insurance)
        - Wear and tear, maintenance issues
        - Damage from wars or civil unrest
        - Intentional damage
        - Most water damage from plumbing (unless sudden)
        - Damage from lack of maintenance
        
        Coverage Limits:
        - Jewelry: $5,000 aggregate limit
        - Cash/Securities: $500 limit
        - Business property: $5,000 limit
        - Property in transit: Limited coverage
        """,
    ],
    
    "auto": [
        """
        AUTO INSURANCE BASIC COVERAGE
        
        Liability Coverage:
        - Bodily Injury: $25,000 per person / $50,000 per accident
        - Property Damage: $25,000 per accident
        - Recommended: Higher limits like 100/300/100
        
        Collision Coverage:
        - Covers damage from accidents with other vehicles
        - Deductible: $500 or $1,000 (you choose)
        - Pays actual cash value of vehicle
        
        Comprehensive Coverage:
        - Covers theft, vandalism, weather, animals
        - Deductible: $250 or $500
        
        Uninsured/Underinsured Motorist:
        - Protects you if hit by uninsured driver
        - Recommended same limits as liability
        """,
        
        """
        AUTO INSURANCE DISCOUNTS & BENEFITS
        
        Available Discounts:
        - Multi-policy discount: 10-15%
        - Safe driver discount: 5-10%
        - Low mileage discount: 5-15%
        - Good student discount: 3-10%
        - Safety feature discount: 5-10%
        - Paperless discount: 5%
        
        Additional Benefits:
        - Roadside assistance (24/7)
        - Rental car coverage: $30/day, max $900
        - Glass coverage: 100% after deductible
        - New car replacement: Up to 150% of vehicle value for 1st year
        """,
    ],
    
    "life": [
        """
        TERM LIFE INSURANCE OVERVIEW
        
        Coverage Periods:
        - 10-year term: $30-50/month for $500K (age 30)
        - 20-year term: $50-80/month for $500K (age 30)
        - 30-year term: $80-120/month for $500K (age 30)
        
        Death Benefit:
        - Tax-free lump sum payment to beneficiaries
        - Guaranteed payout if policy is active
        - No cash value (term only)
        
        Underwriting Process:
        - Medical exam (blood, urine, height/weight)
        - Health history review
        - Lifestyle questions
        - Processing time: 2-4 weeks
        """,
        
        """
        LIFE INSURANCE CLAIMS PROCESS
        
        Steps to File a Claim:
        1. Notify insurer within 30 days of death
        2. Complete claim form (provided by insurer)
        3. Submit required documents:
           - Death certificate (certified copy)
           - Beneficiary proof of ID
           - Proof of relationship to deceased
        4. Insurer reviews and verifies claim
        5. Payment issued within 30-45 days
        
        Exclusions:
        - Death within 2 years due to suicide (returns premiums only)
        - Death while committing a crime
        - Death from illegal activities
        - Non-disclosure of material health information
        
        Grace Period: 30 days to pay missed premiums
        """,
    ],
}

def get_sample_data(insurance_type: str = None):
    \"\"\"Get sample insurance data for seeding\"\"\"
    if insurance_type:
        return INSURANCE_SAMPLES.get(insurance_type, [])
    
    # Flatten all samples
    all_samples = []
    for samples_list in INSURANCE_SAMPLES.values():
        all_samples.extend(samples_list)
    return all_samples
