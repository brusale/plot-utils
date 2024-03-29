import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep

from utils.makeRatio import makeRatio
from utils.handleUncertainties import handleUncertainties
from config.configuration import configuration

class PurityPlots:
    def __init__ (self, 
                  lc_dict_arr, cp_dict_arr,
                  annotate=None,
                  legend=None,
                  c=['red', 'black'],
                  save=None):

        self.lc_dict_arr = lc_dict_arr
        self.cp_dict_arr = cp_dict_arr

        self.annotate=annotate
        self.legend=legend
        self.c = c
        self.save = save
        
        self.metric_label = { 0 : ["Purity", "purity"], 1 : ["Duplicate", "duplicate"] }
        self.eta_bins = np.linspace(-1.4, 1.4, 10)
        self.phi_bins = np.linspace(-np.pi, np.pi, 12)
        self.energy_bins = np.linspace(0, 600, 10)

        self.makePlot(0) # make purity plots
        self.makePlot(1) # make duplicate rate plots
    def makePlot(self, metric):
        fig, axs = plt.subplots(1, 3, figsize=(30, 15))
        for cp_dict, k in zip(self.cp_dict_arr, range(0, len(self.cp_dict_arr))):
            eta_pur, phi_pur, energy_pur = count(cp_dict)
        
            num_eta_counts, _ = np.histogram(eta_pur[0][metric], bins=self.eta_bins)            
            denom_eta_counts, _ = np.histogram(eta_pur[1], bins=self.eta_bins)            
           
            eta_ratio, eta_ratio_error = makeRatio(num_eta_counts, denom_eta_counts)
            eta_ratio_error = handleUncertainties(eta_ratio, eta_ratio_error)
            axs[0].errorbar(self.eta_bins[:-1], \
                            eta_ratio, yerr=eta_ratio_error, \
                            fmt=".", markersize=20, color=self.c[k], \
                            label=self.legend[k])
            axs[0].set_xlabel(r"$\eta$")
            axs[0].set_xlim(-1.2, 1.2) 
       
            num_phi_counts, _ = np.histogram(phi_pur[0][metric], bins=self.phi_bins)            
            denom_phi_counts, _ = np.histogram(phi_pur[1], bins=self.phi_bins)            
                                                                                            
            phi_ratio, phi_ratio_error = makeRatio(num_phi_counts, denom_phi_counts)
            phi_ratio_error = handleUncertainties(phi_ratio, phi_ratio_error)
            axs[1].errorbar(self.phi_bins[:-1], \
                            phi_ratio, yerr=phi_ratio_error, \
                            fmt=".", markersize=20, color=self.c[k], \
                            label=self.legend[k])
            axs[1].set_xlabel(r"$\phi$")
            axs[1].set_xlim(-np.pi, np.pi) 

            num_energy_counts, _ = np.histogram(energy_pur[0][metric], bins=self.energy_bins)            
            denom_energy_counts, _ = np.histogram(energy_pur[1], bins=self.energy_bins)            
                                                                                            
            energy_ratio, energy_ratio_error = makeRatio(num_energy_counts, denom_energy_counts)
            energy_ratio_error = handleUncertainties(energy_ratio, energy_ratio_error)
            axs[2].errorbar(self.energy_bins[:-1], \
                            energy_ratio, yerr=energy_ratio_error, \
                            fmt=".", markersize=20, color=self.c[k], \
                            label=self.legend[k])
            axs[2].set_xlabel(r"Energy (sim) [GeV]")

        for ax in axs:
            hep.cms.text(text=configuration["cmsText"], ax=ax)
            ax.set_ylim(-1e-2, 1.1)
            ax.set_ylabel(self.metric_label[metric][0])
            ax.grid(True)
            ax.legend()
            if self.annotate != None:
                if "Energy (sim) [GeV]" not in ax.get_xlabel():
                    ax.annotate(text=self.annotate, xy=(ax.get_xlim()[0]*0.9, 0.4), fontsize=20)
                else:
                    ax.annotate(text=self.annotate, xy=(ax.get_xlim()[1]*0.2, 0.4), fontsize=20)

        if (self.save != None and len(self.c) == 2):
            fig.savefig(self.save+"%s_comparison.pdf" % self.metric_label[metric][1])
        elif (self.save != None):
            fig.savefig(self.save+"%s.pdf" % self.metric_label[metric][1])

        fig.clf()
 
def count(cp_dict):
    num_eta, denom_eta = [], []
    num_phi, denom_phi = [], []
    num_energy, denom_energy = [], []
    
    num_dup_eta, num_dup_phi, num_dup_energy = [], [], []

    for event in range(0, len(cp_dict)):
        event = str(event+1)
        for cp in range(len(cp_dict[event]['CaloParticleEnergy'])):
            if len(cp_dict[event]['CP2LCscore'][cp]) == 0 : continue
            denom_eta.append(cp_dict[event]['CaloParticleEta'][cp])
            denom_phi.append(cp_dict[event]['CaloParticlePhi'][cp])
            denom_energy.append(cp_dict[event]['CaloParticleEnergy'][cp])
            n_associated_lcs = 0
            for score in cp_dict[event]['CP2LCscore'][cp]:
                if score < 0.2:
                    n_associated_lcs += 1
            if n_associated_lcs > 0:
                num_eta.append(cp_dict[event]['CaloParticleEta'][cp])         
                num_phi.append(cp_dict[event]['CaloParticlePhi'][cp])
                num_energy.append(cp_dict[event]['CaloParticleEnergy'][cp])
                if n_associated_lcs > 1:
                    num_dup_eta.append(cp_dict[event]['CaloParticleEta'][cp])
                    num_dup_phi.append(cp_dict[event]['CaloParticlePhi'][cp])
                    num_dup_energy.append(cp_dict[event]['CaloParticleEnergy'][cp])

    return [[num_eta, num_dup_eta], denom_eta], [[num_phi, num_dup_phi], denom_phi], [[num_energy, num_dup_energy], denom_energy]
