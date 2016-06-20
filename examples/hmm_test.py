import numpy as np
from pyroomacoustics import HMM, CircularGaussianEmission, GaussianEmission

if __name__ == '__main__':

    K = 4
    O = 6
    model = 'left-right'
    leftright_jump_max = K
    n_examples = 200
    example_size = np.arange(40,60)

    # create our Ground truth model
    hmm = HMM(K, 
            CircularGaussianEmission(K,O), 
            model=model,
            leftright_jump_max=leftright_jump_max)

    # Draw a 100 examples
    examples = []
    for i in range(n_examples):
        N = np.random.choice(example_size)
        examples.append(hmm.generate(N))

    # Now create a new model and train it
    emission2 = CircularGaussianEmission(K, O, examples=examples)
    hmm2 = HMM(K, emission2, model=model)

    # We want to properly initialize all parameters
    X = np.concatenate(examples, axis=0) # put all examples in big array

    # Initialize for a left right model
    hmm2.pi[:] = 0
    hmm2.pi[0] = 1
    hmm2.A[:,:] = np.triu(np.tril(np.random.uniform(size=(K,K)), k=K))
    hmm2.A[:,:] += np.diag(np.sum(hmm2.A[:,:], axis=1)*2)
    # Normalize the distributions
    for row in hmm2.A:
        row[:] /= row.sum()
    hmm2.pi[:] /= hmm2.pi.sum()

    # Initialize the emission parameters to mean and variance of dataset
    emission2.mu[:,:] = np.array([np.mean(X, axis=0)]*K)
    centered = X - emission2.mu[0]
    emission2.Sigma[:,:] = np.array([np.mean(centered**2, axis=0)]*K)

    # Now try to fit the model
    niter = hmm2.fit(examples, tol=1e-8, max_iter=1000)

    print 'EM finished in {0} iterations'.format(niter)

    for k in range(K):
        print 'True mu:',hmm.emission.mu[k],'Estimated:',hmm2.emission.mu[k]

    print 'hmm A:',hmm.A
    print 'hmm2 A:',hmm2.A
